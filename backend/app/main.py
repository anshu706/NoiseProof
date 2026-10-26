"""
main.py – FastAPI application entry point.

Endpoints:
  POST /api/runs          – start a pipeline run
  GET  /api/runs/{id}     – poll run status/progress
  GET  /api/results/summary – aggregated metrics for charts
  GET  /api/calls         – list available calls
  GET  /api/calls/{id}    – call details + paths
  POST /api/analyze       – upload and analyse a custom audio file
  GET  /api/usage         – API credit usage counter

Audio files are served statically from data/calls/.
"""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .gnani_client import get_usage, transcribe as stt_transcribe
from .models import AnalysisResult, RunConfig, RunProgress, RunStatus
from .pipeline import get_run, list_runs, start_pipeline
from .summarize import summarise_transcript

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NoiseProof API",
    description="Benchmark for call summarisation under noisy conditions – powered by Gnani AI.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static audio files ────────────────────────────────────────────────────────
if settings.data_dir.exists():
    app.mount("/data", StaticFiles(directory=str(settings.data_dir)), name="data")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "dry_run": settings.dry_run}


# ── Run management ────────────────────────────────────────────────────────────

@app.post("/api/runs", status_code=202)
async def create_run(config: RunConfig, background_tasks: BackgroundTasks) -> dict:
    """Start a new benchmark pipeline run asynchronously."""
    import uuid
    from . import pipeline as _pl
    from .models import RunProgress, RunStatus

    run_id = str(uuid.uuid4())
    progress = RunProgress(
        run_id=run_id,
        status=RunStatus.pending,
        total_steps=config.num_calls * len(config.snr_levels) * len(config.noise_types),
        completed_steps=0,
        current_step="Queued",
    )
    _pl._runs[run_id] = progress

    def _run_task():
        start_pipeline(config, run_id=run_id)

    background_tasks.add_task(_run_task)

    return {"run_id": run_id, "status": "pending"}


@app.get("/api/runs")
async def get_all_runs() -> List[dict]:
    return [r.model_dump() for r in list_runs()]


@app.get("/api/runs/{run_id}")
async def get_run_status(run_id: str) -> dict:
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.model_dump()


# ── Results ───────────────────────────────────────────────────────────────────

@app.get("/api/results/summary")
async def get_results_summary() -> dict:
    """Return aggregated metrics for all completed runs."""
    result_files = sorted(settings.results_dir.glob("*_aggregated.json"), key=lambda p: p.stat().st_mtime)
    if not result_files:
        return {"aggregated": [], "eval": []}

    latest = result_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        aggregated = json.load(f)

    # Also load per-call eval
    eval_file = latest.parent / latest.name.replace("_aggregated", "_eval")
    eval_data = []
    if eval_file.exists():
        with open(eval_file, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

    return {"aggregated": aggregated, "eval": eval_data}


# ── Calls ─────────────────────────────────────────────────────────────────────

@app.get("/api/calls")
async def list_calls() -> List[dict]:
    calls = []
    for call_dir in sorted(settings.calls_dir.iterdir()):
        if not call_dir.is_dir():
            continue
        script_path = call_dir / "script.json"
        if script_path.exists():
            with open(script_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            calls.append({
                "call_id": call_dir.name,
                "scenario": data.get("scenario", ""),
                "turns": len(data.get("script", [])),
                "outcome": data.get("outcome", ""),
            })
    return calls


@app.get("/api/calls/{call_id}")
async def get_call(call_id: str) -> dict:
    call_dir = settings.calls_dir / call_id
    if not call_dir.exists():
        raise HTTPException(status_code=404, detail="Call not found")

    script_path = call_dir / "script.json"
    ref_path = call_dir / "reference_transcript.txt"
    clean_path = call_dir / "clean.wav"

    data: dict[str, Any] = {"call_id": call_id}

    if script_path.exists():
        with open(script_path, "r", encoding="utf-8") as f:
            data["script"] = json.load(f)

    if ref_path.exists():
        data["reference_transcript"] = ref_path.read_text(encoding="utf-8")

    if clean_path.exists():
        data["clean_audio_url"] = f"/data/calls/{call_id}/clean.wav"

    # List available noisy variants
    noisy_files = list(call_dir.glob("noisy_*.wav"))
    data["noisy_variants"] = [
        f"/data/calls/{call_id}/{p.name}" for p in sorted(noisy_files)
    ]

    # Load transcripts
    transcript_files = list((settings.results_dir / call_id).glob("[!summary]*.json"))
    transcripts = []
    for tf in sorted(transcript_files):
        with open(tf, "r", encoding="utf-8") as f:
            transcripts.append(json.load(f))
    data["transcripts"] = transcripts

    return data


# ── Custom upload analysis ────────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze_audio(file: UploadFile = File(...)) -> dict:
    """Upload a custom audio file for transcription + summarisation."""
    import time

    audio_bytes = await file.read()
    if len(audio_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    t0 = time.perf_counter()
    try:
        stt_resp = stt_transcribe(
            audio_bytes=audio_bytes,
            language_code="hi-IN",
            fmt="transcribe",
        )
        transcript = stt_resp.get("transcript", "")
        latency_ms = stt_resp.get("latency_ms", (time.perf_counter() - t0) * 1000)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")

    try:
        summary_result = summarise_transcript(
            call_id="upload",
            noise_type="custom",
            snr="unknown",
            transcript=transcript,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Summarisation failed: {exc}")

    return AnalysisResult(
        filename=file.filename or "upload",
        transcript=transcript,
        summary=summary_result.summary,
        action_items=summary_result.action_items,
        key_facts=summary_result.key_facts,
        sentiment=summary_result.sentiment,
        latency_ms=latency_ms,
        word_count=len(transcript.split()),
    ).model_dump()


# ── Usage ─────────────────────────────────────────────────────────────────────

@app.get("/api/usage")
async def api_usage() -> dict:
    return get_usage()


# ── Frontend static files / SPA ───────────────────────────────────────────────
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    if hasattr(app, "frontend"):
        app.frontend("/", directory=str(frontend_dist), fallback="index.html")
    else:
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True,
    )

