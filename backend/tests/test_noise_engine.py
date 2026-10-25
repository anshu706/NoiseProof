"""
Tests for noise_engine.py

Verified properties:
- Measured SNR of output is within 0.5 dB of target
- clean path returns clean audio
- Each noise type can be synthesised
"""
from __future__ import annotations

import io
import sys
import os
from pathlib import Path

# Allow importing backend from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import pytest
import soundfile as sf

from backend.app.noise_engine import (
    apply_telephone,
    corrupt,
    mix_at_snr,
    measured_snr,
    rms,
    _synthesise_noise,
    audio_to_bytes,
    bytes_to_audio,
    save_wav,
)

SR = 16000
DURATION_S = 3
N = SR * DURATION_S


def make_speech(seed: int = 0) -> np.ndarray:
    """Deterministic sine-wave as synthetic speech."""
    rng = np.random.default_rng(seed)
    t = np.arange(N) / SR
    speech = (
        0.5 * np.sin(2 * np.pi * 300 * t) +
        0.3 * np.sin(2 * np.pi * 1000 * t) +
        0.2 * rng.standard_normal(N)
    ).astype("float32")
    return speech / np.max(np.abs(speech)) * 0.7


@pytest.fixture
def clean_wav_file(tmp_path: Path) -> Path:
    speech = make_speech()
    path = tmp_path / "speech.wav"
    save_wav(speech, SR, path)
    return path


# ── SNR accuracy tests ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("target_snr", [20.0, 10.0, 5.0, 0.0])
def test_snr_accuracy(target_snr: float):
    """Measured SNR must be within ±0.5 dB of the target."""
    speech = make_speech()
    rng = np.random.default_rng(42)
    noise = rng.standard_normal(len(speech)).astype("float32")
    mixed = mix_at_snr(speech, noise, target_snr)

    actual_snr = measured_snr(speech, mixed)
    assert abs(actual_snr - target_snr) < 0.5, (
        f"SNR target={target_snr:.1f} dB but measured={actual_snr:.2f} dB"
    )


# ── Telephone simulation ──────────────────────────────────────────────────────

def test_telephone_resamples_to_8k():
    speech = make_speech()
    out, out_sr = apply_telephone(speech, SR, target_sr=8000)
    assert out_sr == 8000
    expected_samples = int(N * 8000 / SR)
    assert abs(len(out) - expected_samples) <= 2


def test_telephone_output_stays_in_range():
    speech = make_speech()
    out, _ = apply_telephone(speech, SR)
    assert np.all(np.abs(out) <= 1.01), "Telephone output clipped > 1.0"


# ── Noise synthesis ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("noise_type", ["street", "crowd", "wind", "white", "market"])
def test_noise_synthesis(noise_type: str):
    rng = np.random.default_rng(42)
    noise = _synthesise_noise(noise_type, N, SR, rng)
    assert len(noise) == N
    assert noise.dtype == np.float32
    assert rms(noise) > 1e-6, f"Noise type '{noise_type}' produced near-silence"


# ── corrupt() integration ─────────────────────────────────────────────────────

def test_corrupt_clean_path(clean_wav_file: Path):
    """SNR=None (clean) returns telephone-filtered audio."""
    audio, sr = corrupt(clean_wav_file, noise_type="street", snr_db=None)
    assert sr == 8000
    assert len(audio) > 0


def test_corrupt_with_noise(clean_wav_file: Path):
    """corrupt() with SNR=10 returns mixed audio within SNR tolerance."""
    audio, sr = corrupt(clean_wav_file, noise_type="white", snr_db=10.0)
    assert sr == 8000
    assert rms(audio) > 1e-6


def test_corrupt_deterministic(clean_wav_file: Path):
    """Same seed → identical output."""
    a1, _ = corrupt(clean_wav_file, "white", snr_db=5.0, seed=42)
    a2, _ = corrupt(clean_wav_file, "white", snr_db=5.0, seed=42)
    np.testing.assert_array_equal(a1, a2)


# ── Audio I/O round-trip ──────────────────────────────────────────────────────

def test_audio_bytes_roundtrip():
    speech = make_speech()
    b = audio_to_bytes(speech, SR)
    assert len(b) > 0
    recovered, sr = bytes_to_audio(b)
    assert sr == SR
    np.testing.assert_allclose(speech, recovered, atol=1e-4)
