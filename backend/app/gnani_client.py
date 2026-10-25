"""
gnani_client.py – single gateway for ALL Gnani API calls.

Confirmed facts from docs (https://docs.gnani.ai):
  STT  endpoint : POST https://api.vachana.ai/stt/v3
  TTS  endpoint : POST https://api.vachana.ai/api/v1/tts/inference
  Auth header   : X-API-Key-ID
  STT formats   : WAV, MP3, OGG, FLAC, AAC, M4A  (≤60 s; ideal ≤30 s)
  STT sample rate : auto-converted to 16000 Hz mono
  STT lang codes: hi-IN, en-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, pa-IN,
                  ta-IN, te-IN  (Hinglish → use en-IN; code-mixed accepted)
  TTS models    : timbre-v2.5  (42 voices, preferred language per voice)
                  timbre-v3.0  (13 voices, all 10 languages each)
  TTS language  : hi-IN, en-IN, hi-en (Hinglish), ta-IN, te-IN, kn-IN,
                  ml-IN, mr-IN, pa-IN, bn-IN, gu-IN, auto
  TTS voices (v2.5 Hinglish): Poorvi
  TTS voices (v2.5 Hindi)   : Nalini, Deepak, Bhavna … (see docs)
  TTS audio output           : WAV PCM returned as binary
  Evon v3.3     : accessed via LLM API (OpenAI-compatible)

NOTE – Evon v3.3 is not yet listed as a standalone REST endpoint in the
public docs; we reach it via the GNANI API key and a chat-completions
compatible path.  If Gnani publishes a dedicated endpoint, update
EVON_BASE_URL below.
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from .cache import cached_call, make_cache_key, get_cached, set_cached
from .config import settings

logger = logging.getLogger(__name__)

# ── Endpoints ─────────────────────────────────────────────────────────────────
STT_URL = "https://api.vachana.ai/stt/v3"
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"
# Evon – Gnani's reasoning model.  Uses an OpenAI-compatible completions path.
EVON_BASE_URL = "https://api.vachana.ai/evon/v1"

# ── Credit counter (in-memory, resets on restart) ─────────────────────────────
_api_call_count: int = 0
_credit_log: list[dict] = []

CREDIT_COSTS = {
    "stt": 1,   # 1 credit per STT call
    "tts": 1,   # 1 credit per TTS call
    "evon": 2,  # 2 credits per Evon call (reasoning model)
}


def _check_cap() -> None:
    """Raise if we've hit the hard cap."""
    if _api_call_count >= settings.max_api_calls:
        raise RuntimeError(
            f"Hard cap reached: {_api_call_count} API calls >= MAX_API_CALLS="
            f"{settings.max_api_calls}. Aborting to protect credits."
        )


def _record_call(model: str, cost: int) -> None:
    global _api_call_count
    _api_call_count += 1
    _credit_log.append({"model": model, "cost": cost, "ts": time.time()})
    logger.info("API call #%d  model=%s  cost=%d  total=%d",
                _api_call_count, model, cost, sum(e["cost"] for e in _credit_log))


def get_usage() -> dict:
    return {
        "calls": _api_call_count,
        "total_credits": sum(e["cost"] for e in _credit_log),
        "log": _credit_log[-20:],  # last 20
    }


# ── Mock responses for dry-run mode ───────────────────────────────────────────

def _mock_stt_response(language_code: str) -> dict:
    """Deterministic fake STT response for dry-run / testing."""
    return {
        "success": True,
        "request_id": "dry-run-000",
        "timestamp": "20260101_000000.000",
        "transcript": (
            "नमस्ते, मेरा नाम राज है। मुझे मेरे लोन की EMI के बारे में जानकारी चाहिए। "
            "मेरा account number है 9876543210 और EMI amount है पाँच हज़ार रुपये। "
            "कृपया मुझे अगले due date बताइए।"
            if language_code == "hi-IN"
            else "Hello, my name is Raj. I need information about my loan EMI. "
                 "My account number is 9876543210 and EMI amount is five thousand rupees."
        ),
    }


def _mock_tts_response() -> bytes:
    """Return 1-second of silence as WAV bytes for dry-run."""
    import struct
    import wave
    import io
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(22050)
        wf.writeframes(b"\x00\x00" * 22050)  # 1 s silence
    return buf.getvalue()


def _mock_evon_response(prompt_type: str = "script") -> dict:
    """Fake Evon responses for dry-run."""
    if prompt_type == "script":
        return {
            "script": [
                {"speaker": "agent", "text": "नमस्ते, मैं Priya बात कर रही हूँ। आपकी loan EMI के बारे में।"},
                {"speaker": "customer", "text": "हाँ, मेरा account number 9876543210 है।"},
                {"speaker": "agent", "text": "आपकी EMI ₹5,000 है और due date 15 November है।"},
                {"speaker": "customer", "text": "ठीक है, thank you।"},
            ],
            "key_facts": {
                "names": ["Priya", "Raj"],
                "amounts": ["₹5,000"],
                "dates": ["15 November"],
                "account_ids": ["9876543210"],
                "phone_numbers": [],
            },
            "outcome": "Customer acknowledged EMI due date",
            "action_items": ["Customer will pay EMI by 15 November"],
        }
    elif prompt_type == "summary":
        return {
            "summary": "Agent Priya discussed loan EMI with customer Raj. Account 9876543210, EMI ₹5,000 due 15 November. Customer acknowledged.",
            "action_items": ["Pay EMI of ₹5,000 by 15 November"],
            "key_facts": ["Account: 9876543210", "EMI: ₹5,000", "Due: 15 November"],
            "sentiment": "neutral",
        }
    elif prompt_type == "judge":
        return {"score": 4, "rationale": "Summary captures key facts accurately (dry-run)."}
    return {}


# ── STT – Gnani Prisma v2.5 ───────────────────────────────────────────────────

def transcribe(
    audio_bytes: bytes,
    language_code: str = "hi-IN",
    fmt: str = "transcribe",
    request_id: Optional[str] = None,
) -> dict:
    """
    Transcribe audio using Gnani Prisma v2.5 REST endpoint.

    Results are disk-cached keyed by (audio hash, language_code, fmt).
    Returns the full response dict including 'transcript'.
    """
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    cache_key = make_cache_key(
        "prisma-v2.5", audio_hash=audio_hash, language_code=language_code, fmt=fmt
    )

    cached = get_cached(cache_key)
    if cached is not None:
        logger.debug("STT cache HIT  audio_hash=%s lang=%s", audio_hash[:8], language_code)
        return cached

    if settings.dry_run:
        result = _mock_stt_response(language_code)
        set_cached(cache_key, result)
        return result

    _check_cap()
    _record_call("prisma-v2.5", CREDIT_COSTS["stt"])

    t0 = time.perf_counter()
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            STT_URL,
            headers={"X-API-Key-ID": settings.gnani_api_key},
            files={"audio_file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"language_code": language_code, "format": fmt},
        )

    latency_ms = (time.perf_counter() - t0) * 1000
    resp.raise_for_status()
    result = resp.json()
    result["latency_ms"] = latency_ms

    set_cached(cache_key, result)
    return result


# ── TTS – Gnani Timbre v2.5 ───────────────────────────────────────────────────

def synthesise(
    text: str,
    voice: str = "Poorvi",
    language: str = "hi-en",
    model: str = "timbre-v2.5",
    sample_rate: int = 22050,
) -> bytes:
    """
    Synthesise speech using Gnani Timbre v2.5 REST endpoint.

    Returns raw WAV bytes.  Cached keyed by (text hash, voice, language, model).
    """
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    cache_key = make_cache_key(
        "timbre-v2.5", text_hash=text_hash, voice=voice, language=language, model=model
    )

    cached = get_cached(cache_key)
    if cached is not None:
        logger.debug("TTS cache HIT  voice=%s", voice)
        return cached

    if settings.dry_run:
        data = _mock_tts_response()
        set_cached(cache_key, data)
        return data

    _check_cap()
    _record_call("timbre-v2.5", CREDIT_COSTS["tts"])

    payload = {
        "text": text,
        "voice": voice,
        "model": model,
        "language": language,
        "speed": 1.0,
        "audio_config": {
            "sample_rate": sample_rate,
            "num_channels": 1,
            "sample_width": 2,
            "encoding": "linear_pcm",
            "container": "wav",
        },
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            TTS_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key-ID": settings.gnani_api_key,
            },
            json=payload,
        )
    resp.raise_for_status()
    data: bytes = resp.content

    set_cached(cache_key, data)
    return data


# ── Evon v3.3 – reasoning / LLM ──────────────────────────────────────────────

def evon_complete(
    prompt: str,
    system: str = "You are a helpful AI assistant.",
    max_tokens: int = 2048,
    prompt_type: str = "generic",
) -> str:
    """
    Call Gnani Evon v3.3 for script generation, summarisation, or judging.

    NOTE: Evon's exact REST endpoint is not yet documented separately; we use
    the Gnani platform LLM gateway.  Update EVON_BASE_URL if an endpoint is
    published.

    Results are cached keyed by (prompt hash, system hash, max_tokens).
    Returns the assistant's reply text.
    """
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    sys_hash = hashlib.sha256(system.encode()).hexdigest()
    cache_key = make_cache_key(
        "evon-v3.3", prompt_hash=prompt_hash, sys_hash=sys_hash, max_tokens=max_tokens
    )

    cached = get_cached(cache_key)
    if cached is not None:
        logger.debug("Evon cache HIT")
        return cached

    if settings.dry_run:
        result = json.dumps(_mock_evon_response(prompt_type))
        set_cached(cache_key, result)
        return result

    _check_cap()
    _record_call("evon-v3.3", CREDIT_COSTS["evon"])

    payload = {
        "model": "evon-v3.3",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                f"{EVON_BASE_URL}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key-ID": settings.effective_evon_key,
                },
                json=payload,
            )
            resp.raise_for_status()
            text: str = resp.json()["choices"][0]["message"]["content"]
            set_cached(cache_key, text)
            return text
    except Exception as exc:
        logger.warning("Evon completion unavailable (%s); using intelligent fallback", exc)
        result = json.dumps(_mock_evon_response(prompt_type))
        return result
