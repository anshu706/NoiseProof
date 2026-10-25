"""
pipeline.py – End-to-end benchmark pipeline orchestration.

Runs the full loop:
  1. Generate synthetic calls (Evon + Timbre)
  2. Corrupt audio (noise engine)
  3. Transcribe (Prisma)
  4. Summarise (Evon)
  5. Evaluate (metrics)
  6. Save aggregated results

Designed to run in a FastAPI background task with progress callbacks.
"""
from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Callable, List, Optional

from .call_generator import generate_calls
from .config import settings
from .metrics import (
    aggregate_by_snr,
    compute_action_item_f1,
    compute_cer,
    compute_key_fact_recall,
    compute_summary_score,
    compute_wer,
)
from .models import (
    AggregatedMetrics,
    EvalResult,
    RunConfig,
    RunProgress,
    RunStatus,
)
from .summarize import summarise_reference, summarise_transcript
from .transcribe import transcribe_all_variants

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[RunProgress], None]

# In-memory run state (keyed by run_id)
_runs: dict[str, RunProgress] = {}


def get_run(run_id: str) -> Optional[RunProgress]:
    return _runs.get(run_id)


def list_runs() -> list[RunProgress]:
    return list(_runs.values())


def start_pipeline(
    config: RunConfig,
    progress_cb: Optional[ProgressCallback] = None,
    run_id: Optional[str] = None,
) -> str:
    """Launch a benchmark pipeline run and return the run_id."""
    if run_id is None:
        run_id = str(uuid.uuid4())
    noise_types = config.noise_types
    snr_levels = config.snr_levels
    n_calls = config.num_calls

    total = n_calls * len(noise_types) * len(snr_levels)
    progress = _runs.get(run_id)
    if progress is None:
        progress = RunProgress(
            run_id=run_id,
            status=RunStatus.running,
            total_steps=total,
            completed_steps=0,
            current_step="Initialising",
        )
        _runs[run_id] = progress
    else:
        progress.status = RunStatus.running
        progress.total_steps = total
        progress.completed_steps = 0
        progress.current_step = "Initialising"

    # Override dry_run per run config
    if config.dry_run:
        settings.dry_run = True

    def _update(step: str, increment: int = 1):
        progress.current_step = step
        progress.completed_steps += increment
        if progress_cb:
            progress_cb(progress)

    try:
        # ── Step 1: Generate call scripts and audio ────────────────────────
        _update("Generating call scripts", 0)
        scripts = generate_calls(n=n_calls)

        eval_results: list[EvalResult] = []

        for cs in scripts:
            call_dir = settings.calls_dir / cs.call_id
            clean_wav = call_dir / "clean.wav"
            ref_path = call_dir / "reference_transcript.txt"

            # Reference transcript
            if ref_path.exists():
                reference_text = ref_path.read_text(encoding="utf-8")
            else:
                reference_text = "\n".join(
                    f"[{t.speaker.upper()}] {t.text}" for t in cs.script
                )

            # Ideal summary (reference)
            _update(f"Summarising reference for {cs.call_id}", 0)
            ref_summary = summarise_reference(cs.call_id, reference_text)

            # ── Loop over noise types × SNR ────────────────────────────────
            for noise_type in noise_types:
                for snr in snr_levels:
                    step_label = f"{cs.call_id} | {noise_type} @ {snr}dB"
                    logger.info("Processing: %s", step_label)

                    # Transcribe
                    transcript_result = transcribe_all_variants(
                        call_id=cs.call_id,
                        clean_wav=clean_wav,
                        noise_types=[noise_type],
                        snr_levels=[snr],
                    )[0]

                    # Summarise
                    summary_result = summarise_transcript(
                        call_id=cs.call_id,
                        noise_type=noise_type,
                        snr=snr,
                        transcript=transcript_result.transcript,
                    )

                    # Metrics
                    wer = compute_wer(reference_text, transcript_result.transcript)
                    cer = compute_cer(reference_text, transcript_result.transcript)
                    recall = compute_key_fact_recall(
                        cs.key_facts.all_facts(),
                        transcript_result.transcript,
                        " ".join(summary_result.key_facts),
                    )
                    f1 = compute_action_item_f1(
                        cs.action_items, summary_result.action_items
                    )
                    score = compute_summary_score(
                        ref_summary.summary, summary_result.summary
                    )

                    eval_results.append(
                        EvalResult(
                            call_id=cs.call_id,
                            noise_type=noise_type,
                            snr=snr,
                            wer=wer,
                            cer=cer,
                            key_fact_recall=recall,
                            action_item_f1=f1,
                            summary_score=score,
                            latency_ms=transcript_result.latency_ms,
                        )
                    )
                    _update(step_label)

        # ── Save aggregated results ────────────────────────────────────────
        aggregated = aggregate_by_snr(eval_results)
        out_path = settings.results_dir / f"run_{run_id}_aggregated.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                [a.model_dump() for a in aggregated],
                f,
                indent=2,
                ensure_ascii=False,
            )

        # Save per-call eval results
        eval_path = settings.results_dir / f"run_{run_id}_eval.json"
        with open(eval_path, "w", encoding="utf-8") as f:
            json.dump(
                [e.model_dump() for e in eval_results],
                f,
                indent=2,
                ensure_ascii=False,
            )

        progress.status = RunStatus.done
        progress.result_summary = {
            "aggregated": [a.model_dump() for a in aggregated],
            "total_calls": n_calls,
            "total_variants": len(eval_results),
        }

    except Exception as exc:
        logger.exception("Pipeline run %s failed", run_id)
        progress.status = RunStatus.failed
        progress.error = str(exc)

    finally:
        if progress_cb:
            progress_cb(progress)

    return run_id
