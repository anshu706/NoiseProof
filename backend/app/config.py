"""
config.py – centralised settings loaded from .env / environment variables.

All other modules import `settings` from here; no module reads env vars
directly.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Gnani credentials ─────────────────────────────────────────────────────
    gnani_api_key: str = ""
    evon_api_key: str = ""

    # ── Safety caps ───────────────────────────────────────────────────────────
    max_api_calls: int = 200
    dry_run: bool = False

    # ── Experiment defaults ───────────────────────────────────────────────────
    num_base_calls: int = 6
    snr_levels: str = "clean,20,10,5,0"
    noise_types: str = "street,crowd,wind,white,market"

    # ── Paths ─────────────────────────────────────────────────────────────────
    data_dir: Path = Path("data")
    cache_dir: Path = Path("data/cache")

    # ── App ───────────────────────────────────────────────────────────────────
    backend_port: int = 8000
    frontend_port: int = 5173

    @property
    def effective_evon_key(self) -> str:
        """Return Evon key, falling back to GNANI_API_KEY."""
        return self.evon_api_key or self.gnani_api_key

    @property
    def snr_levels_list(self) -> List[str]:
        return [s.strip() for s in self.snr_levels.split(",")]

    @property
    def noise_types_list(self) -> List[str]:
        return [s.strip() for s in self.noise_types.split(",")]

    @property
    def calls_dir(self) -> Path:
        return self.data_dir / "calls"

    @property
    def results_dir(self) -> Path:
        return self.data_dir / "results"

    @property
    def noise_dir(self) -> Path:
        return self.data_dir / "noise"


# Singleton – import and use throughout the app.
settings = Settings()

# Ensure required directories exist at import time.
for _dir in (
    settings.data_dir,
    settings.cache_dir,
    settings.calls_dir,
    settings.results_dir,
    settings.noise_dir,
):
    _dir.mkdir(parents=True, exist_ok=True)
