"""Parse call transcript text into structured fields for n8n workflow ingestion.

The Proposal and Onboarding agents expect transcripts pre-parsed into a
canonical dict so that the Claude extraction prompt receives clean input
rather than raw unstructured text, reducing token usage and hallucination risk.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_SPEAKER_RE = re.compile(r"^([A-Z][^:]{1,40}):\s*(.+)$", re.MULTILINE)
_FILLER_WORDS = frozenset({"um", "uh", "like", "you know", "so", "basically", "actually"})


@dataclass
class ParsedTranscript:
    """Structured representation of a sales call transcript."""

    raw_text: str
    speakers: list[str] = field(default_factory=list)
    turns: list[dict] = field(default_factory=list)
    word_count: int = 0
    duration_estimate_minutes: float | None = None

    def to_dict(self) -> dict:
        return {
            "speakers": self.speakers,
            "turns": self.turns,
            "word_count": self.word_count,
            "duration_estimate_minutes": self.duration_estimate_minutes,
            "cleaned_text": self._cleaned_text(),
        }

    def _cleaned_text(self) -> str:
        """Return the transcript with filler words removed and whitespace normalised."""
        text = self.raw_text
        for filler in _FILLER_WORDS:
            text = re.sub(rf"\b{re.escape(filler)}\b", "", text, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", text).strip()


def parse_transcript(text: str) -> ParsedTranscript:
    """Parse a raw transcript string into a ``ParsedTranscript``.

    Detects speaker turns using ``SPEAKER: text`` patterns. Falls back to
    treating the entire text as a single block if no speakers are found.

    Args:
        text: Raw transcript text, e.g. from a call recording service.

    Returns:
        ``ParsedTranscript`` with speaker list, turn-by-turn breakdown,
        word count, and duration estimate.

    Raises:
        ValueError: If *text* is empty or whitespace-only.
    """
    if not text or not text.strip():
        raise ValueError("Transcript text must not be empty")

    cleaned = _normalize_whitespace(text)
    matches = list(_SPEAKER_RE.finditer(cleaned))

    if matches:
        turns = [
            {"speaker": m.group(1).strip(), "text": m.group(2).strip()}
            for m in matches
        ]
        speakers = _dedupe_ordered([t["speaker"] for t in turns])
    else:
        turns = [{"speaker": "Unknown", "text": cleaned}]
        speakers = ["Unknown"]

    word_count = len(cleaned.split())
    # Assume ~130 words per minute for a business call.
    duration = round(word_count / 130, 1) if word_count else None

    return ParsedTranscript(
        raw_text=text,
        speakers=speakers,
        turns=turns,
        word_count=word_count,
        duration_estimate_minutes=duration,
    )


def extract_action_items(transcript: ParsedTranscript) -> list[str]:
    """Heuristically extract action items from transcript turns.

    Looks for phrases like "I'll", "we'll", "will send", "will follow up",
    "action item", "next step". For production, replace with an LLM call.

    Args:
        transcript: A ``ParsedTranscript`` instance.

    Returns:
        List of sentence strings that appear to be commitments or action items.
    """
    action_patterns = re.compile(
        r"\b(I'll|we'll|will send|will follow[- ]up|action item|next step|I'll make sure|"
        r"I'll get|we'll get back|I'll send over|I'll schedule)\b",
        re.IGNORECASE,
    )
    results = []
    for turn in transcript.turns:
        sentences = re.split(r"(?<=[.!?])\s+", turn["text"])
        for sent in sentences:
            if action_patterns.search(sent):
                results.append(f"[{turn['speaker']}] {sent.strip()}")
    return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return re.sub(r"[^\S\n]+", " ", text).strip()


def _dedupe_ordered(items: list[str]) -> list[str]:
    seen: set = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
