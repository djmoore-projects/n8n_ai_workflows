"""Tests for lead_normalizer."""

from __future__ import annotations

import pytest

from src.data_prep.lead_normalizer import normalize_lead, normalize_leads_csv


# ---------------------------------------------------------------------------
# normalize_lead
# ---------------------------------------------------------------------------


def test_basic_normalization():
    raw = {
        "first_name": "  Jane ",
        "last_name": "  Doe",
        "email": "JANE@EXAMPLE.COM",
        "company": "Acme Corp",
        "source": "linkedin",
        "stage": "warm",
    }
    result = normalize_lead(raw)
    assert result["first_name"] == "Jane"
    assert result["last_name"] == "Doe"
    assert result["email"] == "jane@example.com"
    assert result["company"] == "Acme Corp"
    assert result["lead_source"] == "linkedin"
    assert result["engagement_stage"] == "warm"


def test_id_generated_when_missing():
    raw = {"email": "test@test.com"}
    result = normalize_lead(raw)
    assert result["id"]
    assert len(result["id"]) == 36  # UUID4 format


def test_id_preserved_when_present():
    raw = {"id": "abc-123", "email": "test@test.com"}
    result = normalize_lead(raw)
    assert result["id"] == "abc-123"


def test_phone_normalized():
    raw = {"email": "a@b.com", "phone": "(555) 123-4567"}
    result = normalize_lead(raw)
    assert result["phone"] == "5551234567"


def test_phone_international_prefix_preserved():
    raw = {"email": "a@b.com", "phone": "+1 (800) 555-0100"}
    result = normalize_lead(raw)
    assert result["phone"].startswith("+")
    assert "800" in result["phone"]


def test_missing_contact_raises():
    with pytest.raises(ValueError, match="contact method"):
        normalize_lead({"first_name": "No", "last_name": "Contact"})


def test_unknown_stage_defaults_to_cold():
    raw = {"email": "x@y.com", "engagement_stage": "maybe-someday"}
    result = normalize_lead(raw)
    assert result["engagement_stage"] == "cold"


def test_source_alias_resolved():
    raw = {"email": "x@y.com", "source": "LI"}
    result = normalize_lead(raw)
    assert result["lead_source"] == "linkedin"


def test_status_defaults_to_new():
    raw = {"email": "x@y.com"}
    result = normalize_lead(raw)
    assert result["status"] == "new"


# ---------------------------------------------------------------------------
# normalize_leads_csv
# ---------------------------------------------------------------------------


def test_csv_round_trip():
    csv_text = (
        "id,first_name,last_name,email,company,source,stage\n"
        "1,Alice,Smith,alice@corp.com,Corp,website,warm\n"
        "2,Bob,Jones,bob@co.com,Co,referral,cold\n"
    )
    results = normalize_leads_csv(csv_text)
    assert len(results) == 2
    assert results[0]["email"] == "alice@corp.com"
    assert results[1]["lead_source"] == "referral"


def test_csv_skips_invalid_rows(capsys):
    csv_text = (
        "first_name,last_name\n"
        "No,Contact\n"
        "Also,NoContact\n"
    )
    results = normalize_leads_csv(csv_text)
    assert results == []
    captured = capsys.readouterr()
    assert "Skipping row" in captured.out
