"""Core discrepancy checks for conversion tracking integrity."""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


SEVERITY_ORDER = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
    Severity.INFO: 4,
}


@dataclass
class Finding:
    check_id: str
    title: str
    severity: Severity
    description: str
    evidence: str
    recommendation: str
    transaction_ids: list[str] = field(default_factory=list)
    effort_minutes: int = 15
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
            "transaction_ids": self.transaction_ids,
            "effort_minutes": self.effort_minutes,
            "tags": self.tags,
        }


def run_all_checks(events: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_duplicate_purchases(events))
    findings.extend(check_missing_transactions(events))
    findings.extend(check_value_mismatches(events))
    findings.extend(check_consent_gaps(events))
    findings.extend(check_source_coverage(events))
    return sorted(findings, key=lambda f: (SEVERITY_ORDER[f.severity], f.check_id))


def check_duplicate_purchases(events: list[dict]) -> list[Finding]:
    """Same transaction_id appearing more than once within a source, or conflicting across sources."""
    findings = []
    by_source_tid: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    for e in events:
        if e["event_name"] not in ("purchase", "purchase_event", "conversion"):
            continue
        tid = e["transaction_id"]
        if not tid:
            continue
        by_source_tid[e["source"]][tid].append(e)

    # Duplicates within the same source
    for source, tids in by_source_tid.items():
        for tid, occurrences in tids.items():
            if len(occurrences) > 1:
                findings.append(
                    Finding(
                        check_id="DUP-001",
                        title=f"Duplicate purchase events in {source}",
                        severity=Severity.HIGH,
                        description=(
                            f"Transaction `{tid}` appears {len(occurrences)} times in {source}. "
                            "This commonly inflates conversion counts and ROAS."
                        ),
                        evidence=f"source={source}, transaction_id={tid}, count={len(occurrences)}",
                        recommendation=(
                            "Ensure only one purchase event fires per order. Common causes: "
                            "both native Shopify Google channel + custom GTM tag, or thank-you page "
                            "reloads without a once-only guard. Deduplicate in GTM or disable the "
                            "duplicate source."
                        ),
                        transaction_ids=[tid],
                        effort_minutes=20,
                        tags=["duplicates", "attribution"],
                    )
                )

    return findings


def check_missing_transactions(events: list[dict]) -> list[Finding]:
    """Transactions present in one source but missing in another (when multiple sources exist)."""
    findings = []
    sources = sorted({e["source"] for e in events if e.get("source")})
    if len(sources) < 2:
        return findings

    # Build set of transaction_ids per source (purchase events only)
    tids_by_source: dict[str, set[str]] = defaultdict(set)
    for e in events:
        if e["event_name"] not in ("purchase", "purchase_event", "conversion"):
            continue
        tid = e["transaction_id"]
        if tid:
            tids_by_source[e["source"]].add(tid)

    # Compare pairwise against the richest source as reference
    ref_source = max(tids_by_source.keys(), key=lambda s: len(tids_by_source[s]))
    ref_tids = tids_by_source[ref_source]

    for source in sources:
        if source == ref_source:
            continue
        missing = ref_tids - tids_by_source[source]
        if missing:
            sample = sorted(missing)[:5]
            findings.append(
                Finding(
                    check_id="MIS-001",
                    title=f"Missing purchases in {source}",
                    severity=Severity.HIGH,
                    description=(
                        f"{len(missing)} transaction(s) present in `{ref_source}` are missing from `{source}`. "
                        "This under-reports conversions and can cause under-bidding or wrong optimization."
                    ),
                    evidence=f"reference={ref_source}, missing_in={source}, count={len(missing)}, sample={sample}",
                    recommendation=(
                        "Verify the purchase tag/event is firing on the order confirmation page for all "
                        "order types (including express checkout, Shop Pay, etc.). Check consent mode "
                        "and ad blockers as possible causes of missing browser-side events. Consider "
                        "server-side / Measurement Protocol backup for critical revenue."
                    ),
                    transaction_ids=sample,
                    effort_minutes=30,
                    tags=["missing-events", "attribution"],
                )
            )

    return findings


def check_value_mismatches(events: list[dict]) -> list[Finding]:
    """Same transaction_id with different revenue values across sources."""
    findings = []
    values: dict[str, dict[str, float]] = defaultdict(dict)  # tid -> {source: value}

    for e in events:
        if e["event_name"] not in ("purchase", "purchase_event", "conversion"):
            continue
        tid = e["transaction_id"]
        val = e["value"]
        if not tid or val is None:
            continue
        values[tid][e["source"]] = val

    for tid, source_vals in values.items():
        if len(source_vals) < 2:
            continue
        unique_vals = set(round(v, 2) for v in source_vals.values())
        if len(unique_vals) > 1:
            findings.append(
                Finding(
                    check_id="VAL-001",
                    title=f"Revenue value mismatch for order {tid}",
                    severity=Severity.HIGH,
                    description=(
                        f"Transaction `{tid}` has different reported values across sources: {source_vals}. "
                        "This distorts ROAS and can cause budget to be allocated to the wrong campaigns."
                    ),
                    evidence=str(source_vals),
                    recommendation=(
                        "Align value calculation: decide whether to send order total, subtotal, or "
                        "net revenue (after discounts/shipping/tax). Ensure currency is consistent. "
                        "In Shopify + GA4, confirm the data layer / tag is using the same money field "
                        "as Google Ads conversion value."
                    ),
                    transaction_ids=[tid],
                    effort_minutes=25,
                    tags=["value-mismatch", "revenue"],
                )
            )

    return findings


def check_consent_gaps(events: list[dict]) -> list[Finding]:
    """Flag events that look like they fired without consent when consent field is present."""
    findings = []
    no_consent = [
        e for e in events
        if e.get("consent") is not None
        and str(e["consent"]).lower() in ("denied", "false", "0", "no", "refused")
        and e["event_name"] in ("purchase", "purchase_event", "conversion")
    ]
    if no_consent:
        tids = [e["transaction_id"] for e in no_consent if e["transaction_id"]][:5]
        findings.append(
            Finding(
                check_id="CON-001",
                title="Purchase events recorded with denied consent",
                severity=Severity.MEDIUM,
                description=(
                    f"{len(no_consent)} purchase event(s) appear to have been recorded while consent "
                    "was denied. This may violate consent mode expectations and create inconsistent "
                    "attribution between consented and non-consented traffic."
                ),
                evidence=f"count={len(no_consent)}, sample_transaction_ids={tids}",
                recommendation=(
                    "Review Consent Mode v2 implementation. Ensure purchase tags respect "
                    "ad_storage / analytics_storage signals. Consider modeled conversions "
                    "in Google Ads for consented-only measurement gaps."
                ),
                transaction_ids=tids,
                effort_minutes=20,
                tags=["consent", "privacy"],
            )
        )
    return findings


def check_source_coverage(events: list[dict]) -> list[Finding]:
    """Informational: which sources are present and basic volume."""
    findings = []
    by_source = defaultdict(int)
    for e in events:
        if e["event_name"] in ("purchase", "purchase_event", "conversion"):
            by_source[e["source"]] += 1

    if not by_source:
        findings.append(
            Finding(
                check_id="COV-001",
                title="No purchase events found",
                severity=Severity.CRITICAL,
                description="No events with event_name indicating a purchase were found in the provided data.",
                evidence=f"total_events={len(events)}",
                recommendation="Confirm the export contains purchase/conversion events and column names are recognized.",
                effort_minutes=10,
                tags=["coverage"],
            )
        )
        return findings

    summary = ", ".join(f"{s}: {c}" for s, c in sorted(by_source.items()))
    findings.append(
        Finding(
            check_id="COV-002",
            title="Source coverage summary",
            severity=Severity.INFO,
            description=f"Purchase event counts by source — {summary}",
            evidence=summary,
            recommendation="Use this as a baseline. Large imbalances between Shopify orders and GA4/Ads purchases usually indicate a tracking gap.",
            effort_minutes=0,
            tags=["coverage"],
        )
    )
    return findings