"""
call_generator.py – Synthetic Hinglish call generation.

Uses Evon v3.3 to write call scripts (JSON) then Timbre v2.5 to synthesise
each speaker turn into audio, concatenating them with short pauses to form
a realistic mono call recording.

Voices:
  Agent    → Poorvi (Hinglish female, professional)
  Customer → Vikrant (Hindi male, conversational)
"""
from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Optional

import numpy as np
import soundfile as sf

from . import gnani_client as gc
from .cache import make_cache_key, get_cached, set_cached
from .config import settings
from .models import CallScript, KeyFacts, SpeakerTurn
from .noise_engine import audio_to_bytes, bytes_to_audio

logger = logging.getLogger(__name__)

AGENT_VOICE = "Poorvi"       # Hinglish female
CUSTOMER_VOICE = "Vikrant"   # Hindi male, warm conversational

SILENCE_MS = 400   # pause between turns

SCENARIOS = [
    "loan EMI reminder – customer missed payment, agent discusses overdue amount and next steps",
    "delivery complaint – customer says order hasn't arrived after 7 days, agent checks tracking",
    "insurance renewal – agent reminds customer policy expires in 10 days, discusses premium",
    "bank card block request – customer reports lost card, agent verifies identity and blocks it",
    "mobile recharge issue – customer's recharge of ₹199 hasn't reflected, agent investigates",
    "mutual fund SIP query – customer asks about pausing SIP, agent explains process and charges",
]

SCRIPT_SYSTEM = """You are an expert at generating realistic synthetic Hinglish customer-support call scripts.
Output ONLY valid JSON matching the schema below.  No markdown fences, no extra text.

Schema:
{
  "call_id": "<string>",
  "scenario": "<one-line description>",
  "script": [
    {"speaker": "agent"|"customer", "text": "<natural Hinglish dialogue>"},
    ...
  ],
  "key_facts": {
    "names": ["<name>", ...],
    "amounts": ["₹X,XXX", ...],
    "dates": ["<date>", ...],
    "account_ids": ["<id>", ...],
    "phone_numbers": ["<number>", ...]
  },
  "outcome": "<one sentence>",
  "action_items": ["<action>", ...]
}

Rules:
- 8–14 turns per call, alternating agent and customer
- Mix Hindi and English naturally (code-mixed Hinglish)
- Include realistic key facts (amounts in ₹, dates like "15 November 2026", account numbers)
- Agent always starts and ends the call
- Keep tone professional but conversational
"""


FALLBACK_SCRIPTS = [
    {
        "scenario": "loan EMI reminder",
        "script": [
            {"speaker": "agent", "text": "नमस्ते Raj जी, मैं Priya बात कर रही हूँ Apex Bank से। क्या मेरी बात Raj Sharma से हो रही है?"},
            {"speaker": "customer", "text": "हाँ Priya जी, बोलिए, क्या बात है?"},
            {"speaker": "agent", "text": "सर, आपके personal loan account number 9876543210 का EMI payment pending है।"},
            {"speaker": "customer", "text": "अच्छा, कितना amount due है और due date क्या है?"},
            {"speaker": "agent", "text": "सर total EMI amount ₹5,000 है और last due date 15 November 2026 थी।"},
            {"speaker": "customer", "text": "ठीक है, मैं आज शाम तक net banking से ₹5,000 transfer कर दूँगा।"},
            {"speaker": "agent", "text": "बहुत धन्यवाद Raj जी। Payment होते ही confirmation SMS आपके mobile number 9820012345 पर आ जाएगा। Have a nice day!"},
            {"speaker": "customer", "text": "Thank you Priya जी, bye."}
        ],
        "key_facts": {
            "names": ["Priya", "Raj Sharma"],
            "amounts": ["₹5,000"],
            "dates": ["15 November 2026"],
            "account_ids": ["9876543210"],
            "phone_numbers": ["9820012345"]
        },
        "outcome": "Customer promised to pay pending loan EMI of ₹5,000 by evening",
        "action_items": ["Customer to pay ₹5,000 by net banking", "Bank to send confirmation SMS to 9820012345"]
    },
    {
        "scenario": "delivery complaint",
        "script": [
            {"speaker": "agent", "text": "Hello, QuickCart support में आपका स्वागत है, मेरा नाम Ankit है। मैं आपकी क्या सहायता कर सकता हूँ?"},
            {"speaker": "customer", "text": "Ankit जी, मैंने एक package order किया था 18 October को, order ID है OD87654321। सात दिन हो गए, delivery नहीं मिली।"},
            {"speaker": "agent", "text": "मुझे असुविधा के लिए खेद है Kavita जी। मैं system में check कर रहा हूँ, order amount ₹2,499 था।"},
            {"speaker": "customer", "text": "हाँ, prepaid payment था ₹2,499 का। मुझे urgent delivery चाहिए।"},
            {"speaker": "agent", "text": "Kavita जी, package local hub पर पहुंच चुका है। मैंने priority dispatch mark कर दिया है, 24 hours में deliver हो जाएगा।"},
            {"speaker": "customer", "text": "क्या delivery boy मुझे call करेगा dispatch के समय?"},
            {"speaker": "agent", "text": "जी बिल्कुल, delivery agent आपके number 9930054321 पर call करेगा।"},
            {"speaker": "customer", "text": "Alright, thank you Ankit."},
            {"speaker": "agent", "text": "Thank you for contacting QuickCart support. Have a great day!"}
        ],
        "key_facts": {
            "names": ["Ankit", "Kavita"],
            "amounts": ["₹2,499"],
            "dates": ["18 October", "24 hours"],
            "account_ids": ["OD87654321"],
            "phone_numbers": ["9930054321"]
        },
        "outcome": "Agent expedited delayed delivery and scheduled dispatch within 24 hours",
        "action_items": ["Priority dispatch OD87654321 from local hub", "Delivery agent to call 9930054321"]
    },
    {
        "scenario": "insurance renewal",
        "script": [
            {"speaker": "agent", "text": "नमस्ते Deepak जी, मैं Neha बात कर रही हूँ SecureLife Insurance से।"},
            {"speaker": "customer", "text": "हाँ Neha जी, बताइए क्या notification है?"},
            {"speaker": "agent", "text": "सर आपकी car insurance policy number POL-543210 की validity 5 November 2026 को expire हो रही है।"},
            {"speaker": "customer", "text": "अच्छा, इस साल renewal premium amount कितना होगा?"},
            {"speaker": "agent", "text": "No claim bonus discount के बाद annual premium ₹12,500 बनता है सर।"},
            {"speaker": "customer", "text": "क्या 5 November के बाद grace period मिलता है payment के लिए?"},
            {"speaker": "agent", "text": "जी हाँ Deepak जी, 15 days का grace period होता है, पर policy lapse से बचने के लिए 5 November से पहले pay करना safe है।"},
            {"speaker": "customer", "text": "ठीक है Neha जी, मुझे payment link 9811122334 पर WhatsApp कर दीजिए।"},
            {"speaker": "agent", "text": "मैंने link भेज दिया है सर। Thank you for choosing SecureLife!"}
        ],
        "key_facts": {
            "names": ["Neha", "Deepak"],
            "amounts": ["₹12,500"],
            "dates": ["5 November 2026", "15 days"],
            "account_ids": ["POL-543210"],
            "phone_numbers": ["9811122334"]
        },
        "outcome": "Customer agreed to renew policy POL-543210 with ₹12,500 premium",
        "action_items": ["Send WhatsApp renewal payment link to 9811122334", "Deepak to complete renewal payment before 5 November 2026"]
    },
    {
        "scenario": "bank card block request",
        "script": [
            {"speaker": "agent", "text": "Union Bank emergency customer service, मैं Vikram बात कर रहा हूँ। How can I help you?"},
            {"speaker": "customer", "text": "Vikram जी, मेरा debit card metro station पर lost हो गया है, कृपया तुरंत block कर दीजिए।"},
            {"speaker": "agent", "text": "बिल्कुल Sunita जी, सुरक्षा के लिए account number verify करवा दीजिए।"},
            {"speaker": "customer", "text": "मेरा savings account number 1029384756 है और card के last 4 digits 4321 हैं।"},
            {"speaker": "agent", "text": "धन्यवाद Sunita जी, मैंने card ending 4321 permanently block कर दिया है। 25 October 2026 आज की date note कर लीजिए।"},
            {"speaker": "customer", "text": "क्या मुझे new replacement card मिलेगा?"},
            {"speaker": "agent", "text": "हाँ मैम, new chip debit card आपके registered address पर 5 working days में deliver हो जाएगा। Charges ₹250 account से deduct होंगे।"},
            {"speaker": "customer", "text": "ठीक है Vikram जी, confirmation SMS भेज दीजिए 9712345678 पर।"},
            {"speaker": "agent", "text": "SMS भेज दिया गया है Sunita जी। Be assured आपका account safe है।"}
        ],
        "key_facts": {
            "names": ["Vikram", "Sunita"],
            "amounts": ["₹250"],
            "dates": ["25 October 2026", "5 working days"],
            "account_ids": ["1029384756", "4321"],
            "phone_numbers": ["9712345678"]
        },
        "outcome": "Lost debit card successfully blocked and replacement requested",
        "action_items": ["Block debit card ending 4321", "Dispatch replacement card within 5 working days", "Send confirmation SMS to 9712345678"]
    },
    {
        "scenario": "mobile recharge issue",
        "script": [
            {"speaker": "agent", "text": "Airtel Customer Care में आपका स्वागत है, मेरा नाम Sneha है। बताइए क्या समस्या आ रही है?"},
            {"speaker": "customer", "text": "Sneha जी, मैंने कल ₹199 का data recharge कराया था, लेकिन balance update नहीं हुआ।"},
            {"speaker": "agent", "text": "निश्चिंत रहिए Rohan जी, क्या recharge इसी mobile number 9898989898 पर किया था?"},
            {"speaker": "customer", "text": "हाँ, 9898989898 पर ही किया था 24 October को। Transaction ID है TXN987654।"},
            {"speaker": "agent", "text": "मैंने TXN987654 check कर लिया है सर। Payment bank end पर pending थी, जो अभी clear हुई है।"},
            {"speaker": "customer", "text": "तो कब तक data pack activate हो जाएगा?"},
            {"speaker": "agent", "text": "Rohan जी, next 2 hours के अंदर ₹199 का 1.5GB/day pack activate हो जाएगा।"},
            {"speaker": "customer", "text": "Great, thanks Sneha for the quick resolution."},
            {"speaker": "agent", "text": "Thank you Rohan जी, Airtel से जुड़ने के लिए धन्यवाद!"}
        ],
        "key_facts": {
            "names": ["Sneha", "Rohan"],
            "amounts": ["₹199"],
            "dates": ["24 October", "2 hours"],
            "account_ids": ["TXN987654"],
            "phone_numbers": ["9898989898"]
        },
        "outcome": "Agent resolved pending payment for transaction TXN987654",
        "action_items": ["Activate ₹199 pack on 9898989898 within 2 hours", "Send activation confirmation message"]
    },
    {
        "scenario": "mutual fund SIP query",
        "script": [
            {"speaker": "agent", "text": "GrowMax Wealth Advisory, मैं Meera बोल रही हूँ। Good morning sir."},
            {"speaker": "customer", "text": "Good morning Meera जी, मैं Rahul Sen बोल रहा हूँ। मेरी monthly SIP pause करनी है।"},
            {"speaker": "agent", "text": "Sure Rahul जी, आपकी folio number share कर दीजिए please."},
            {"speaker": "customer", "text": "Folio number MF-998877 है, Bluechip Equity Fund। Monthly installment ₹3,000 है।"},
            {"speaker": "agent", "text": "Yes sir, next deduction 10 November 2026 को scheduled है। आप कितने months के लिए pause करना चाहते हैं?"},
            {"speaker": "customer", "text": "3 months के लिए pause करना है, February 2027 से resume हो जाए। क्या कोई penalty charges हैं?"},
            {"speaker": "agent", "text": "नहीं Rahul जी, SIP pause service totally free of charge है, zero penalty। मैंने 3 months pause request register कर दी है।"},
            {"speaker": "customer", "text": "Excellent Meera जी। Confirmation details 9654321890 पर WhatsApp कर दीजिए।"},
            {"speaker": "agent", "text": "ज़रूर Rahul जी, confirmation details भेज दी गई हैं। Thank you for choosing GrowMax!"}
        ],
        "key_facts": {
            "names": ["Meera", "Rahul Sen"],
            "amounts": ["₹3,000", "zero penalty"],
            "dates": ["10 November 2026", "February 2027", "3 months"],
            "account_ids": ["MF-998877"],
            "phone_numbers": ["9654321890"]
        },
        "outcome": "3-month SIP pause registered with zero penalty",
        "action_items": ["Pause SIP on folio MF-998877 until February 2027", "Send WhatsApp confirmation to 9654321890"]
    }
]


def _parse_script(raw_json: str, call_id: str) -> CallScript:
    """Parse Evon JSON output into a CallScript model."""
    # Strip markdown fences if present
    raw_json = re.sub(r"```[a-z]*\n?", "", raw_json).strip()
    data = json.loads(raw_json)
    data["call_id"] = call_id
    kf = data.get("key_facts", {})
    return CallScript(
        call_id=call_id,
        scenario=data.get("scenario", ""),
        script=[SpeakerTurn(**t) for t in data["script"]],
        key_facts=KeyFacts(**kf),
        outcome=data.get("outcome", ""),
        action_items=data.get("action_items", []),
    )


def generate_script(scenario: str, call_id: str) -> CallScript:
    """Ask Evon to write a call script for the given scenario with fallback."""
    try:
        prompt = (
            f'Generate a realistic Hinglish customer-support call script for this scenario:\n\n'
            f'"{scenario}"\n\n'
            f'call_id: "{call_id}"\n\n'
            f'Output only the JSON.'
        )
        raw = gc.evon_complete(prompt, system=SCRIPT_SYSTEM, prompt_type="script")
        return _parse_script(raw, call_id)
    except Exception as exc:
        logger.warning("Using fallback script for %s: %s", call_id, exc)

    # Pick matching fallback script by index or keyword
    idx = 0
    try:
        num = int(re.sub(r"\D", "", call_id))
        idx = (num - 1) % len(FALLBACK_SCRIPTS)
    except Exception:
        idx = 0

    fb = FALLBACK_SCRIPTS[idx].copy()
    fb["call_id"] = call_id
    kf = fb.get("key_facts", {})
    return CallScript(
        call_id=call_id,
        scenario=fb.get("scenario", scenario),
        script=[SpeakerTurn(**t) for t in fb["script"]],
        key_facts=KeyFacts(**kf),
        outcome=fb.get("outcome", ""),
        action_items=fb.get("action_items", []),
    )


def _silence(duration_ms: int, sr: int = 22050) -> np.ndarray:
    return np.zeros(int(duration_ms * sr / 1000), dtype="float32")


def synthesise_call(script: CallScript, output_dir: Path) -> Path:
    """
    Voice each turn with Timbre v2.5, concatenate into one mono WAV.

    Returns path to the saved clean.wav file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    sr = 22050
    segments: list[np.ndarray] = []

    for i, turn in enumerate(script.script):
        voice = AGENT_VOICE if turn.speaker == "agent" else CUSTOMER_VOICE
        # Hinglish for agent, hi-IN for customer
        language = "hi-en" if turn.speaker == "agent" else "hi-IN"

        audio_bytes = gc.synthesise(
            text=turn.text,
            voice=voice,
            language=language,
            sample_rate=sr,
        )
        audio, actual_sr = bytes_to_audio(audio_bytes)

        # Resample if TTS returned different rate
        if actual_sr != sr:
            import scipy.signal as sig_
            n = int(len(audio) * sr / actual_sr)
            audio = sig_.resample(audio, n).astype("float32")

        segments.append(audio)
        if i < len(script.script) - 1:
            segments.append(_silence(SILENCE_MS, sr))

    combined = np.concatenate(segments).astype("float32")
    out_path = output_dir / "clean.wav"
    sf.write(str(out_path), combined, sr, subtype="PCM_16")
    logger.info("Saved clean call audio → %s (%.1f s)", out_path, len(combined) / sr)
    return out_path


def generate_calls(n: int = 2) -> list[CallScript]:
    """
    Generate n synthetic calls end-to-end:
    script → audio → saved to data/calls/<call_id>/.

    Returns list of CallScript objects.
    """
    scripts: list[CallScript] = []
    for i in range(n):
        scenario = SCENARIOS[i % len(SCENARIOS)]
        call_id = f"call_{i+1:03d}"
        call_dir = settings.calls_dir / call_id

        # Check if already generated
        script_path = call_dir / "script.json"
        clean_path = call_dir / "clean.wav"
        ref_path = call_dir / "reference_transcript.txt"

        if script_path.exists() and clean_path.exists():
            logger.info("Call %s already exists, loading from disk", call_id)
            with open(script_path, "r", encoding="utf-8") as f:
                cs = CallScript.model_validate_json(f.read())
        else:
            logger.info("Generating call %s  scenario=%s", call_id, scenario[:40])
            cs = generate_script(scenario, call_id)
            call_dir.mkdir(parents=True, exist_ok=True)

            # Save script
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(cs.model_dump_json(indent=2))

            # Synthesise audio
            synthesise_call(cs, call_dir)

            # Save reference transcript (concatenation of all turns)
            ref_text = "\n".join(
                f"[{t.speaker.upper()}] {t.text}" for t in cs.script
            )
            with open(ref_path, "w", encoding="utf-8") as f:
                f.write(ref_text)

        scripts.append(cs)

    return scripts
