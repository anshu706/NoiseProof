"""
metrics.py – Evaluation metrics for the NoiseProof benchmark.

Metrics computed per (call, noise_type, SNR):
  1. WER  – Word Error Rate  (jiwer)
  2. CER  – Character Error Rate (jiwer)
  3. Key-fact recall – fuzzy + number-aware matching
  4. Action-item F1  – Evon-as-judge (1 cached call per set)
  5. Summary quality score (1–5) – Evon judge with fixed rubric

Text normalisation:
  - Lowercase
  - Strip punctuation
  - Roman Hinglish assumed (Prisma en-IN / hi-IN outputs Roman for code-mixed)
  - Devanagari preserved for hi-IN pure output; comparison is character-level
    to handle script differences correctly
"""
from __future__ import annotations

import json
import logging
import re
import unicodedata
from typing import List, Optional

import jiwer

from . import gnani_client as gc
from .models import AggregatedMetrics, EvalResult, SummaryResult

logger = logging.getLogger(__name__)

# ── Text normalisation ────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace.
    Devanagari letters are kept; only punctuation is removed.
    """
    text = text.lower()
    # Remove punctuation (but preserve Devanagari characters and digits)
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── WER / CER ─────────────────────────────────────────────────────────────────

def compute_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate using jiwer."""
    if not reference.strip():
        return 1.0
    ref = _normalise(reference)
    hyp = _normalise(hypothesis)
    if not hyp.strip():
        return 1.0
    return float(jiwer.wer(ref, hyp))


def compute_cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate using jiwer."""
    if not reference.strip():
        return 1.0
    ref = _normalise(reference)
    hyp = _normalise(hypothesis)
    if not hyp.strip():
        return 1.0
    return float(jiwer.cer(ref, hyp))


# ── Key-fact recall ───────────────────────────────────────────────────────────

def _normalise_amount(s: str) -> str:
    """Normalise currency: ₹5,000 → 5000."""
    s = re.sub(r"[₹,\s]", "", s)
    # spoken form → digit
    word_map = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0",
        "ten": "10", "hundred": "100", "thousand": "1000", "lakh": "100000",
    }
    for w, d in word_map.items():
        s = re.sub(rf"\b{w}\b", d, s, flags=re.IGNORECASE)
    return s.lower().strip()


def _fact_match(fact: str, text: str) -> bool:
    """
    Return True if `fact` appears in `text` using:
    1. Exact substring (normalised)
    2. Amount normalisation for monetary values
    3. Token-level partial match (all tokens present)
    """
    fact_norm = _normalise(fact)
    text_norm = _normalise(text)

    if fact_norm in text_norm:
        return True

    # Amount comparison
    if any(c.isdigit() for c in fact):
        fact_num = _normalise_amount(fact)
        text_num = _normalise_amount(text)
        if fact_num and fact_num in text_num:
            return True

    # Token-level: all tokens of fact appear somewhere in text
    tokens = fact_norm.split()
    if tokens and all(t in text_norm for t in tokens):
        return True

    return False


def compute_key_fact_recall(
    ground_truth_facts: List[str],
    transcript: str,
    summary: str,
) -> float:
    """
    Fraction of ground-truth key facts found in transcript OR summary.
    Returns 1.0 if no facts to check.
    """
    if not ground_truth_facts:
        return 1.0
    combined = transcript + " " + summary
    found = sum(1 for f in ground_truth_facts if _fact_match(f, combined))
    return found / len(ground_truth_facts)


# ── Action-item F1 (Evon judge) ───────────────────────────────────────────────

JUDGE_SYSTEM_ACTION = """You are evaluating whether predicted action items match reference action items.

For each predicted action item, output 1 (match) or 0 (no match).
A match means the predicted item covers the same intent as a reference item.

Output ONLY a JSON object:
{"matches": [<1_or_0>, ...], "tp": <int>, "fp": <int>, "fn": <int>}

tp = true positives, fp = false positives, fn = false negatives"""


def compute_action_item_f1(
    reference_actions: List[str],
    predicted_actions: List[str],
) -> float:
    """
    Compute F1 score for action items using Evon as judge.
    Falls back to simple recall if Evon unavailable.
    """
    if not reference_actions:
        return 1.0 if not predicted_actions else 0.5
    if not predicted_actions:
        return 0.0

    prompt = (
        f"Reference action items:\n{json.dumps(reference_actions)}\n\n"
        f"Predicted action items:\n{json.dumps(predicted_actions)}\n\n"
        f"Evaluate matches."
    )
    try:
        raw = gc.evon_complete(
            prompt, system=JUDGE_SYSTEM_ACTION, prompt_type="judge"
        )
        data = json.loads(re.sub(r"```[a-z]*\n?", "", raw).strip())
        tp = int(data.get("tp", 0))
        fp = int(data.get("fp", 0))
        fn = int(data.get("fn", 0))
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        return float(f1)
    except Exception as e:
        logger.warning("Evon action-item judge failed: %s – falling back to recall", e)
        # Fallback: simple token recall
        found = sum(
            1 for ref in reference_actions
            if any(_fact_match(ref, pred) for pred in predicted_actions)
        )
        return found / len(reference_actions)


# ── Summary quality score (Evon judge) ────────────────────────────────────────

JUDGE_SYSTEM_SUMMARY = """You are a call summary quality judge.
Rate the predicted summary against the reference summary on a scale of 1–5.

Rubric:
5 – All key facts correct, complete, faithful, no hallucination
4 – Minor omissions, no factual errors
3 – Some key facts missing or slightly imprecise
2 – Major omissions or factual errors
1 – Completely wrong, hallucinated, or empty

Output ONLY JSON: {"score": <1-5>, "rationale": "<one sentence>"}"""


def compute_summary_score(reference_summary: str, predicted_summary: str) -> float:
    """
    Ask Evon to rate the predicted summary vs the reference on a 1–5 scale.
    """
    if not predicted_summary.strip():
        return 1.0

    prompt = (
        f"Reference summary:\n{reference_summary}\n\n"
        f"Predicted summary:\n{predicted_summary}\n\n"
        f"Rate on 1–5 scale."
    )
    try:
        raw = gc.evon_complete(
            prompt, system=JUDGE_SYSTEM_SUMMARY, prompt_type="judge"
        )
        data = json.loads(re.sub(r"```[a-z]*\n?", "", raw).strip())
        return float(data.get("score", 3))
    except Exception as e:
        logger.warning("Evon summary judge failed: %s", e)
        # Fallback: WER-based proxy (higher WER → lower score)
        w = compute_wer(reference_summary, predicted_summary)
        return max(1.0, 5.0 - w * 4.0)


# ── Aggregation ───────────────────────────────────────────────────────────────

def aggregate_by_snr(results: List[EvalResult]) -> List[AggregatedMetrics]:
    """Compute mean ± std of each metric grouped by SNR level."""
    import numpy as np

    snr_groups: dict[str, list[EvalResult]] = {}
    for r in results:
        snr_groups.setdefault(r.snr, []).append(r)

    aggregated = []
    for snr, group in sorted(snr_groups.items()):
        wers = [r.wer for r in group]
        cers = [r.cer for r in group]
        recalls = [r.key_fact_recall for r in group]
        f1s = [r.action_item_f1 for r in group]
        scores = [r.summary_score for r in group]
        latencies = [r.latency_ms for r in group]

        aggregated.append(
            AggregatedMetrics(
                snr=snr,
                wer_mean=float(np.mean(wers)),
                wer_std=float(np.std(wers)),
                cer_mean=float(np.mean(cers)),
                key_fact_recall_mean=float(np.mean(recalls)),
                key_fact_recall_std=float(np.std(recalls)),
                action_item_f1_mean=float(np.mean(f1s)),
                summary_score_mean=float(np.mean(scores)),
                latency_ms_mean=float(np.mean(latencies)),
            )
        )
    return aggregated
