"""
noise_engine.py – Local noise generation and audio corruption.

All noise is synthesised procedurally (NumPy) – no external downloads needed.
SNR mixing uses correct RMS-based arithmetic.  Output is deterministic given
a fixed random seed.

Telephone simulation:
  - Resample to 8 kHz
  - Band-pass 300–3400 Hz
  - Optional mild compression / clipping
  - Optional packet-loss dropouts

Supported noise types: street, crowd, wind, white, market
Custom noise .wav files placed in data/noise/ are also picked up automatically.
"""
from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import scipy.signal as sig
import soundfile as sf

from .config import settings

logger = logging.getLogger(__name__)

SEED = 42
RNG = np.random.default_rng(SEED)

# ── Audio helpers ─────────────────────────────────────────────────────────────

def load_wav(path: Path) -> tuple[np.ndarray, int]:
    """Load a WAV file; returns (float32 mono, sample_rate)."""
    data, sr = sf.read(str(path), always_2d=False, dtype="float32")
    if data.ndim == 2:
        data = data.mean(axis=1)
    return data, sr


def save_wav(data: np.ndarray, sr: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), data.astype("float32"), sr, subtype="PCM_16")


def audio_to_bytes(data: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, data.astype("float32"), sr, subtype="PCM_16", format="WAV")
    return buf.getvalue()


def bytes_to_audio(raw: bytes) -> tuple[np.ndarray, int]:
    buf = io.BytesIO(raw)
    return sf.read(buf, always_2d=False, dtype="float32")


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2)) + 1e-9)


# ── Telephone simulation ──────────────────────────────────────────────────────

def _telephone_filter(data: np.ndarray, sr: int) -> np.ndarray:
    """Band-pass 300–3400 Hz (ITU G.711 telephone band)."""
    low = 300 / (sr / 2)
    high = 3400 / (sr / 2)
    # Clamp to valid range
    high = min(high, 0.999)
    b, a = sig.butter(4, [low, high], btype="band")
    return sig.lfilter(b, a, data).astype("float32")


def _resample(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr:
        return data
    n_samples = int(len(data) * target_sr / orig_sr)
    return sig.resample(data, n_samples).astype("float32")


def apply_telephone(
    data: np.ndarray,
    sr: int,
    target_sr: int = 8000,
    clipping_level: float = 0.95,
    dropout_prob: float = 0.01,
    dropout_len_ms: float = 50.0,
    rng: Optional[np.random.Generator] = None,
) -> tuple[np.ndarray, int]:
    """
    Simulate telephone channel degradation:
    1. Resample to target_sr (default 8 kHz).
    2. Band-pass 300–3400 Hz.
    3. Mild soft-clip compression.
    4. Random packet-loss dropouts.
    """
    if rng is None:
        rng = RNG

    # 1. Resample
    data = _resample(data, sr, target_sr)
    sr = target_sr

    # 2. Band-pass
    data = _telephone_filter(data, sr)

    # 3. Soft-clipping (tanh-based)
    data = np.tanh(data / clipping_level) * clipping_level

    # 4. Packet-loss dropouts
    dropout_samples = int(dropout_len_ms * sr / 1000)
    for _ in range(int(len(data) * dropout_prob / dropout_samples) + 1):
        if rng.random() < dropout_prob:
            start = rng.integers(0, max(1, len(data) - dropout_samples))
            data[start : start + dropout_samples] = 0.0

    return data.astype("float32"), sr


# ── Noise synthesis ───────────────────────────────────────────────────────────

def _white_noise(n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.standard_normal(n).astype("float32")


def _pink_noise(n: int, rng: np.random.Generator) -> np.ndarray:
    """Approximate 1/f pink noise via iterative filter."""
    white = rng.standard_normal(n).astype("float64")
    # Simple approximation: apply 1/f^0.5 shaping in frequency domain
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1e-6  # avoid div by zero
    spectrum = np.fft.rfft(white) / np.sqrt(freqs)
    pink = np.fft.irfft(spectrum, n=n)
    return pink.astype("float32")


def _street_noise(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    """Traffic noise: pink base + occasional horn bursts."""
    base = _pink_noise(n, rng)
    # Low-pass filter to mimic traffic rumble
    b, a = sig.butter(3, 2000 / (sr / 2), btype="low")
    base = sig.lfilter(b, a, base).astype("float32")
    # Add horn blasts
    burst_count = max(1, n // (sr * 5))
    for _ in range(burst_count):
        start = rng.integers(0, max(1, n - sr // 2))
        duration = rng.integers(sr // 4, sr // 2)
        freq = rng.uniform(400, 600)
        t = np.arange(duration) / sr
        horn = (0.3 * np.sin(2 * np.pi * freq * t)).astype("float32")
        end = min(start + duration, n)
        base[start:end] += horn[: end - start]
    return base


def _crowd_noise(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    """Babble noise: sum of band-pass filtered white sources."""
    n_voices = 12
    mix = np.zeros(n, dtype="float32")
    for _ in range(n_voices):
        v = rng.standard_normal(n).astype("float32")
        fc_low = rng.uniform(200, 800) / (sr / 2)
        fc_hi = rng.uniform(1500, 4000) / (sr / 2)
        fc_hi = min(fc_hi, 0.999)
        b, a = sig.butter(2, [fc_low, fc_hi], btype="band")
        mix += sig.lfilter(b, a, v).astype("float32")
    return mix / n_voices


def _wind_noise(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    """Wind: low-frequency random with occasional gusts."""
    base = _pink_noise(n, rng)
    b, a = sig.butter(2, 500 / (sr / 2), btype="low")
    base = sig.lfilter(b, a, base).astype("float32")
    # Gusts: amplitude modulation
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.1, 0.5) * np.arange(n) / sr)
    return (base * mod).astype("float32")


def _market_noise(n: int, sr: int, rng: np.random.Generator) -> np.ndarray:
    """Indian market: crowd + random high-freq chatter."""
    crowd = _crowd_noise(n, sr, rng)
    hi = rng.standard_normal(n).astype("float32")
    b, a = sig.butter(2, [3000 / (sr / 2), min(0.999, 6000 / (sr / 2))], btype="band")
    hi = sig.lfilter(b, a, hi).astype("float32")
    return (crowd + 0.3 * hi).astype("float32")


def _synthesise_noise(
    noise_type: str, n: int, sr: int, rng: np.random.Generator
) -> np.ndarray:
    generators = {
        "white": lambda: _white_noise(n, rng),
        "street": lambda: _street_noise(n, sr, rng),
        "crowd": lambda: _crowd_noise(n, sr, rng),
        "wind": lambda: _wind_noise(n, sr, rng),
        "market": lambda: _market_noise(n, sr, rng),
    }
    if noise_type in generators:
        noise = generators[noise_type]()
    else:
        # Try loading custom noise file
        noise_file = settings.noise_dir / f"{noise_type}.wav"
        if noise_file.exists():
            noise_data, noise_sr = load_wav(noise_file)
            noise = _resample(noise_data, noise_sr, sr)
            # Tile/trim to length n
            repeats = int(np.ceil(n / len(noise)))
            noise = np.tile(noise, repeats)[:n]
        else:
            logger.warning("Unknown noise type '%s', using white noise", noise_type)
            noise = _white_noise(n, rng)
    return noise.astype("float32")


# ── SNR mixing ────────────────────────────────────────────────────────────────

def mix_at_snr(
    speech: np.ndarray, noise: np.ndarray, target_snr_db: float
) -> np.ndarray:
    """
    Mix speech + noise at the given SNR (dB) using RMS normalisation.

    SNR_dB = 20 * log10(rms_speech / rms_noise)
    => noise_scale = rms_speech / (rms_noise * 10^(SNR/20))
    """
    speech_rms = rms(speech)
    noise_rms = rms(noise)
    target_noise_rms = speech_rms / (10 ** (target_snr_db / 20))
    scale = target_noise_rms / noise_rms

    # Trim/pad noise to match speech length
    if len(noise) < len(speech):
        repeats = int(np.ceil(len(speech) / len(noise)))
        noise = np.tile(noise, repeats)
    noise = noise[: len(speech)]

    mixed = speech + scale * noise
    # Normalise to prevent clipping
    peak = np.max(np.abs(mixed))
    if peak > 0.99:
        mixed = mixed / peak * 0.99
    return mixed.astype("float32")


def measured_snr(speech: np.ndarray, mixed: np.ndarray) -> float:
    """Estimate SNR of a mixed signal given clean speech reference (dB)."""
    ref = speech[: len(mixed)].astype("float64")
    mix = mixed.astype("float64")
    denom = np.dot(ref, ref)
    if denom > 1e-12:
        alpha = np.dot(mix, ref) / denom
    else:
        alpha = 1.0
    noise_estimate = mix - alpha * ref
    return float(20 * np.log10(rms(alpha * ref) / rms(noise_estimate)))


# ── Public API ────────────────────────────────────────────────────────────────

def corrupt(
    clean_wav: Path,
    noise_type: str,
    snr_db: Optional[float] = None,
    telephone_sim: bool = True,
    seed: int = SEED,
) -> tuple[np.ndarray, int]:
    """
    Load a clean WAV file and produce a noisy degraded version.

    Parameters
    ----------
    clean_wav   : Path to clean mono WAV.
    noise_type  : One of "street", "crowd", "wind", "white", "market", or
                  a filename stem in data/noise/.
    snr_db      : Target SNR in dB.  None = clean (telephone filter only).
    telephone_sim: Apply telephone channel simulation.
    seed        : Random seed for reproducibility.

    Returns (noisy_audio: float32 ndarray, sample_rate: int)
    """
    rng = np.random.default_rng(seed)
    speech, sr = load_wav(clean_wav)

    if telephone_sim:
        speech, sr = apply_telephone(speech, sr, rng=rng)

    if snr_db is None:
        return speech, sr

    noise = _synthesise_noise(noise_type, len(speech), sr, rng)
    noisy = mix_at_snr(speech, noise, snr_db)
    return noisy, sr
