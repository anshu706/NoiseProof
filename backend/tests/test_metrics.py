"""
Tests for metrics.py

Verifies:
- WER/CER on known examples
- Key-fact recall with fuzzy matching
- Normalisation helpers
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest

from backend.app.metrics import (
    compute_cer,
    compute_key_fact_recall,
    compute_wer,
    _fact_match,
    _normalise,
)


# ── WER tests ─────────────────────────────────────────────────────────────────

def test_wer_identical():
    assert compute_wer("hello world", "hello world") == pytest.approx(0.0)


def test_wer_fully_wrong():
    wer = compute_wer("hello world", "foo bar baz")
    assert wer >= 0.5


def test_wer_one_sub():
    wer = compute_wer("hello world", "hello earth")
    assert 0.0 < wer <= 0.6


def test_wer_empty_hypothesis():
    assert compute_wer("hello world", "") == 1.0


def test_wer_empty_reference():
    # undefined – we return 1.0 by convention
    assert compute_wer("", "anything") == 1.0


# ── CER tests ─────────────────────────────────────────────────────────────────

def test_cer_identical():
    assert compute_cer("test", "test") == pytest.approx(0.0)


def test_cer_partial():
    cer = compute_cer("hello world", "hello wrold")
    assert 0.0 < cer < 0.5


# ── Key-fact recall tests ─────────────────────────────────────────────────────

def test_recall_all_found():
    facts = ["Raj", "₹5,000", "15 November"]
    text = "Customer Raj owes ₹5,000, due 15 November."
    assert compute_key_fact_recall(facts, text, "") == pytest.approx(1.0)


def test_recall_none_found():
    facts = ["Priya", "₹12,000", "1 January"]
    text = "No relevant information here."
    assert compute_key_fact_recall(facts, text, "") == pytest.approx(0.0)


def test_recall_partial():
    facts = ["Raj", "₹5,000", "1 December"]
    text = "Customer Raj owes rupees."
    recall = compute_key_fact_recall(facts, text, "")
    assert 0.0 < recall < 1.0


def test_recall_in_summary_not_transcript():
    facts = ["account 9876543210"]
    transcript = "Customer called about his account."
    summary = "Account 9876543210 discussed."
    # Fact found in summary counts
    recall = compute_key_fact_recall(facts, transcript, summary)
    assert recall == pytest.approx(1.0)


def test_recall_empty_facts():
    assert compute_key_fact_recall([], "anything", "") == pytest.approx(1.0)


# ── Fact matching tests ───────────────────────────────────────────────────────

def test_fact_match_exact():
    assert _fact_match("Raj", "customer Raj confirmed")


def test_fact_match_amount_normalised():
    # ₹5,000 vs "five thousand rupees" – not exact, but number present
    assert _fact_match("5000", "the amount is 5000")


def test_fact_match_case_insensitive():
    assert _fact_match("EMI", "the emi is due")


def test_fact_no_match():
    assert not _fact_match("Priya", "hello world")


# ── Normalisation tests ───────────────────────────────────────────────────────

def test_normalise_lowercase():
    assert _normalise("Hello World") == "hello world"


def test_normalise_strips_punctuation():
    assert _normalise("hello, world!") == "hello world"


def test_normalise_collapses_spaces():
    assert _normalise("  hello   world  ") == "hello world"
