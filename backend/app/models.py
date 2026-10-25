"""
models.py – Pydantic data models shared across the backend.
"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class NoiseType(str, Enum):
    street = "street"
    crowd = "crowd"
    wind = "wind"
    white = "white"
    market = "market"


class SNRLevel(str, Enum):
    clean = "clean"
    snr_20 = "20"
    snr_10 = "10"
    snr_5 = "5"
    snr_0 = "0"


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


# ── Script / Call models ───────────────────────────────────────────────────────

class SpeakerTurn(BaseModel):
    speaker: str  # "agent" | "customer"
    text: str


class KeyFacts(BaseModel):
    names: List[str] = []
    amounts: List[str] = []
    dates: List[str] = []
    account_ids: List[str] = []
    phone_numbers: List[str] = []

    def all_facts(self) -> List[str]:
        """Flatten all facts into a single list for recall computation."""
        return (
            self.names
            + self.amounts
            + self.dates
            + self.account_ids
            + self.phone_numbers
        )


class CallScript(BaseModel):
    call_id: str
    scenario: str
    script: List[SpeakerTurn]
    key_facts: KeyFacts
    outcome: str
    action_items: List[str]


# ── Transcript / Result models ─────────────────────────────────────────────────

class TranscriptResult(BaseModel):
    call_id: str
    noise_type: str
    snr: str
    transcript: str
    latency_ms: float = 0.0
    error: Optional[str] = None


class SummaryResult(BaseModel):
    call_id: str
    noise_type: str
    snr: str
    summary: str
    action_items: List[str]
    key_facts: List[str]
    sentiment: str
    error: Optional[str] = None


# ── Metrics models ─────────────────────────────────────────────────────────────

class EvalResult(BaseModel):
    call_id: str
    noise_type: str
    snr: str
    wer: float
    cer: float
    key_fact_recall: float
    action_item_f1: float
    summary_score: float  # 1–5
    latency_ms: float


class AggregatedMetrics(BaseModel):
    snr: str
    wer_mean: float
    wer_std: float
    cer_mean: float
    key_fact_recall_mean: float
    key_fact_recall_std: float
    action_item_f1_mean: float
    summary_score_mean: float
    latency_ms_mean: float


# ── Pipeline run models ───────────────────────────────────────────────────────

class RunConfig(BaseModel):
    num_calls: int = Field(default=2, ge=1, le=10)
    snr_levels: List[str] = Field(default=["clean", "20", "10", "5", "0"])
    noise_types: List[str] = Field(default=["street", "crowd", "wind", "white", "market"])
    dry_run: bool = False


class RunProgress(BaseModel):
    run_id: str
    status: RunStatus
    total_steps: int
    completed_steps: int
    current_step: str = ""
    error: Optional[str] = None
    result_summary: Optional[Dict[str, Any]] = None

    @property
    def pct(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return self.completed_steps / self.total_steps * 100


# ── Upload / custom analysis ──────────────────────────────────────────────────

class AnalysisResult(BaseModel):
    filename: str
    transcript: str
    summary: str
    action_items: List[str]
    key_facts: List[str]
    sentiment: str
    latency_ms: float
    word_count: int
