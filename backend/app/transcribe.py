"""
transcribe.py – Transcription pipeline using Gnani Prisma v2.5.

Sends each noisy audio variant to the STT API (via the caching wrapper),
saves results to data/results/<call_id>/<noise_type>_<snr>.json.
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

from . import gnani_client as gc
from .config import settings
from .models import TranscriptResult
from .noise_engine import audio_to_bytes, corrupt, load_wav, save_wav

logger = logging.getLogger(__name__)

LANGUAGE_CODE = "hi-IN"   # Prisma handles code-mixed Hindi+English on hi-IN

SNR_MAP = {
    "clean": None,
    "20": 20.0,
    "10": 10.0,
    "5": 5.0,
    "0": 0.0,
}


def _result_path(call_id: str, noise_type: str, snr: str) -> Path:
    return settings.results_dir / call_id / f"{noise_type}_{snr}.json"


def _noisy_audio_path(call_id: str, noise_type: str, snr: str) -> Path:
    return settings.calls_dir / call_id / f"noisy_{noise_type}_{snr}.wav"


def transcribe_variant(
    call_id: str,
    clean_wav: Path,
    noise_type: str,
    snr: str,
    force: bool = False,
) -> TranscriptResult:
    """
    Produce and transcribe one noisy variant of a call.

    Steps:
    1. Generate noisy audio (cached on disk).
    2. Send to Prisma v2.5 (cached in diskcache).
    3. Save result JSON.
    """
    result_path = _result_path(call_id, noise_type, snr)
    noisy_path = _noisy_audio_path(call_id, noise_type, snr)

    # Load from disk cache if already done
    if result_path.exists() and not force:
        with open(result_path, "r", encoding="utf-8") as f:
            return TranscriptResult.model_validate_json(f.read())

    # Generate noisy audio
    snr_db = SNR_MAP.get(snr)
    telephone = True  # always apply phone sim

    if noisy_path.exists() and not force:
        audio_bytes = noisy_path.read_bytes()
    else:
        noisy_audio, sr = corrupt(
            clean_wav,
            noise_type=noise_type if snr != "clean" else "white",
            snr_db=snr_db,
            telephone_sim=telephone,
        )
        noisy_path.parent.mkdir(parents=True, exist_ok=True)
        save_wav(noisy_audio, sr, noisy_path)
        audio_bytes = audio_to_bytes(noisy_audio, sr)

    # Transcribe
    try:
        resp = gc.transcribe(
            audio_bytes=audio_bytes,
            language_code=LANGUAGE_CODE,
            fmt="transcribe",
        )
        transcript = resp.get("transcript", "")
        latency_ms = resp.get("latency_ms", 0.0)
        error = None
    except Exception as exc:
        logger.error("STT failed for %s/%s_%s: %s", call_id, noise_type, snr, exc)
        transcript = ""
        latency_ms = 0.0
        error = str(exc)

    result = TranscriptResult(
        call_id=call_id,
        noise_type=noise_type,
        snr=snr,
        transcript=transcript,
        latency_ms=latency_ms,
        error=error,
    )

    result_path.parent.mkdir(parents=True, exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))

    return result


def transcribe_all_variants(
    call_id: str,
    clean_wav: Path,
    noise_types: Optional[list[str]] = None,
    snr_levels: Optional[list[str]] = None,
) -> list[TranscriptResult]:
    """Transcribe every (noise_type × snr) combination for one call."""
    if noise_types is None:
        noise_types = settings.noise_types_list
    if snr_levels is None:
        snr_levels = settings.snr_levels_list

    results: list[TranscriptResult] = []
    for noise_type in noise_types:
        for snr in snr_levels:
            logger.info("Transcribing %s  noise=%s  snr=%s", call_id, noise_type, snr)
            r = transcribe_variant(call_id, clean_wav, noise_type, snr)
            results.append(r)

    return results
