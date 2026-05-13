"""Tests for transcript_parser."""

from __future__ import annotations

import pytest

from src.data_prep.transcript_parser import (
    extract_action_items,
    parse_transcript,
)

SAMPLE_TRANSCRIPT = """\
Derek: Thanks for jumping on the call today. Can you walk me through your current process?
Client: Sure. Right now we do everything manually in spreadsheets. It takes forever.
Derek: I see. What's your timeline for making a change?
Client: We'd like something in place by Q3.
Derek: Great, I'll send over a proposal by end of week. We'll schedule a follow-up then.
Client: Perfect, sounds good.
"""


# ---------------------------------------------------------------------------
# parse_transcript
# ---------------------------------------------------------------------------


def test_speakers_detected():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    assert "Derek" in result.speakers
    assert "Client" in result.speakers


def test_speakers_deduplicated():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    assert len(result.speakers) == len(set(result.speakers))


def test_turns_count():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    assert len(result.turns) == 6


def test_word_count_positive():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    assert result.word_count > 0


def test_duration_estimate_reasonable():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    # At ~130 wpm, this short transcript should be under 5 minutes
    assert result.duration_estimate_minutes is not None
    assert result.duration_estimate_minutes < 5


def test_empty_transcript_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_transcript("")


def test_whitespace_only_raises():
    with pytest.raises(ValueError, match="empty"):
        parse_transcript("   \n\t  ")


def test_no_speaker_format_falls_back():
    blob = "This is a transcript with no speaker labels at all."
    result = parse_transcript(blob)
    assert result.speakers == ["Unknown"]
    assert len(result.turns) == 1


def test_to_dict_has_required_keys():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    d = result.to_dict()
    for key in ("speakers", "turns", "word_count", "duration_estimate_minutes", "cleaned_text"):
        assert key in d, f"Missing key: {key}"


def test_cleaned_text_removes_fillers():
    transcript_with_fillers = (
        "Derek: So, um, basically what I'll do is send you the proposal.\n"
        "Client: Uh, okay."
    )
    result = parse_transcript(transcript_with_fillers)
    cleaned = result._cleaned_text()
    assert "um" not in cleaned.lower()
    assert "uh" not in cleaned.lower()
    assert "basically" not in cleaned.lower()


# ---------------------------------------------------------------------------
# extract_action_items
# ---------------------------------------------------------------------------


def test_action_items_extracted():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    items = extract_action_items(result)
    assert len(items) > 0
    # "I'll send over a proposal" should be captured
    assert any("send" in item.lower() for item in items)


def test_action_items_include_speaker():
    result = parse_transcript(SAMPLE_TRANSCRIPT)
    items = extract_action_items(result)
    # Each item should be prefixed with [Speaker]
    assert all(item.startswith("[") for item in items)


def test_no_action_items_in_plain_chat():
    plain = "Derek: Hello.\nClient: Hi there.\n"
    result = parse_transcript(plain)
    items = extract_action_items(result)
    assert isinstance(items, list)  # Should return empty list, not raise
