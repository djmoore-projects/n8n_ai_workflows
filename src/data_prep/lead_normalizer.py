"""Normalise CRM export CSVs into clean dicts ready for n8n ingestion.

The n8n Sales Lead Agent expects a specific field schema. Raw CRM exports
often have inconsistent casing, trailing whitespace, mixed phone formats,
and missing fields. This module enforces a canonical shape before the data
enters the workflow.
"""

from __future__ import annotations

import csv
import io
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional


_PHONE_RE = re.compile(r"[^\d+]")


def normalize_lead(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize a single raw lead dict into the canonical n8n workflow schema.

    Args:
        raw: Arbitrary dict from a CRM export or API response.

    Returns:
        Normalized lead dict with guaranteed keys and cleaned values.

    Raises:
        ValueError: If the record is missing both ``email`` and ``phone``.
    """
    email = _clean_str(raw.get("email") or raw.get("Email") or "")
    phone = _normalize_phone(raw.get("phone") or raw.get("Phone") or raw.get("mobile") or "")

    if not email and not phone:
        raise ValueError("Lead must have at least one contact method (email or phone)")

    return {
        "id": _clean_str(raw.get("id") or raw.get("lead_id") or "") or str(uuid.uuid4()),
        "first_name": _clean_str(raw.get("first_name") or raw.get("FirstName") or ""),
        "last_name": _clean_str(raw.get("last_name") or raw.get("LastName") or ""),
        "email": email.lower(),
        "phone": phone,
        "company": _clean_str(raw.get("company") or raw.get("Company") or raw.get("account") or ""),
        "lead_source": _normalize_source(raw.get("lead_source") or raw.get("source") or ""),
        "engagement_stage": _normalize_stage(raw.get("engagement_stage") or raw.get("stage") or ""),
        "notes": _clean_str(raw.get("notes") or raw.get("Notes") or ""),
        "created_at": _normalize_date(raw.get("created_at") or raw.get("date_added") or ""),
        "status": _clean_str(raw.get("status") or "new").lower(),
    }


def normalize_leads_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Parse a CSV string of lead records and return a list of normalized dicts.

    Args:
        csv_text: Raw CSV content as a string (with header row).

    Returns:
        List of normalized lead dicts. Rows that fail validation are skipped.
    """
    reader = csv.DictReader(io.StringIO(csv_text))
    results = []
    for i, row in enumerate(reader):
        try:
            results.append(normalize_lead(dict(row)))
        except ValueError as exc:
            # Log and continue rather than aborting the full batch.
            print(f"Skipping row {i + 2}: {exc}")
    return results


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _clean_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _normalize_phone(raw: str) -> str:
    """Strip all non-digit characters except a leading +."""
    clean = _PHONE_RE.sub("", raw)
    if raw.startswith("+"):
        clean = "+" + clean
    return clean


def _normalize_source(raw: str) -> str:
    s = raw.strip().lower()
    aliases = {
        "linkedin": "linkedin",
        "li": "linkedin",
        "referral": "referral",
        "ref": "referral",
        "website": "website",
        "web": "website",
        "cold_email": "cold_email",
        "cold email": "cold_email",
        "inbound": "inbound",
        "event": "event",
        "conference": "event",
    }
    return aliases.get(s, s or "unknown")


def _normalize_stage(raw: str) -> str:
    s = raw.strip().lower()
    valid = {"cold", "warm", "hot", "qualified", "closed"}
    return s if s in valid else "cold"


def _normalize_date(raw: str) -> str:
    if not raw:
        return datetime.now(tz=timezone.utc).isoformat()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(raw.strip(), fmt).replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return raw  # return as-is if unparseable
