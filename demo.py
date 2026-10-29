#!/usr/bin/env python3
"""
Demonstration of the Conversion-Tracking Integrity Audit engine.

Uses synthetic Shopify + GA4 + Google Ads exports that intentionally contain:
- 3 duplicate purchase events
- 2 incorrect revenue values
- 1 missing conversion
"""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import __version__
from engine.loader import load_multi
from engine.checks import run_all_checks
from engine.reporter import write_reports, render_markdown


def main() -> int:
    base = Path(__file__).parent / "sample_data"
    files = [
        base / "shopify_orders.csv",
        base / "ga4_purchases.csv",
        base / "google_ads_conversions.csv",
    ]

    print("=" * 64)
    print("Conversion-Tracking Integrity Audit — Demonstration")
    print(f"Engine v{__version__}")
    print("=" * 64)
    print()
    print("Synthetic data designed to contain:")
    print("  • 3 duplicate purchase events (GA4)")
    print("  • 2 incorrect revenue values")
    print("  • 1 missing conversion (ORD-1006 absent from Google Ads)")
    print()

    events = load_multi(files)
    findings = run_all_checks(events)
    sources = sorted({e["source"] for e in events})
    meta = {"engine_version": __version__, "sources": ", ".join(sources)}

    out_dir = Path(__file__).parent / "reports"
    md_path, json_path = write_reports(findings, out_dir, meta)

    # Detection checklist
    has_dup = any(f.check_id.startswith("DUP") for f in findings)
    has_missing = any(f.check_id.startswith("MIS") for f in findings)
    has_value = any(f.check_id.startswith("VAL") for f in findings)

    print("Detection checklist:")
    print(f"  [ {'x' if has_dup else ' '} ] Duplicate purchases")
    print(f"  [ {'x' if has_missing else ' '} ] Missing conversion(s)")
    print(f"  [ {'x' if has_value else ' '} ] Value mismatches")
    print()
    print(f"Events loaded : {len(events)}")
    print(f"Sources       : {', '.join(sources)}")
    print(f"Findings      : {len(findings)}")
    print(f"Report (MD)   : {md_path}")
    print(f"Report (JSON) : {json_path}")
    print()
    print("-" * 64)
    print(render_markdown(findings, meta))
    print("-" * 64)

    if has_dup and has_missing and has_value:
        print("\nDEMO PASSED — all three required discrepancy types were identified.")
        return 0
    print("\nDEMO INCOMPLETE — one or more required signals missing.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())