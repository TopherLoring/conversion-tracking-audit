#!/usr/bin/env python3
"""CLI for Conversion-Tracking Integrity Audit."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

from . import __version__
from .loader import load_multi
from .checks import run_all_checks
from .reporter import write_reports, render_markdown


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Conversion-Tracking Integrity Audit — find duplicates, missing purchases, value mismatches"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="One or more CSV/JSON event exports (Shopify, GA4, Google Ads, etc.)",
    )
    parser.add_argument("--out", default="reports", help="Output directory (default: reports/)")
    parser.add_argument("--stdout", action="store_true", help="Also print Markdown report")
    args = parser.parse_args(argv)

    paths = [Path(f) for f in args.files]
    for p in paths:
        if not p.exists():
            print(f"Error: file not found: {p}", file=sys.stderr)
            return 1

    events = load_multi(paths)
    findings = run_all_checks(events)
    sources = sorted({e["source"] for e in events})
    meta = {"engine_version": __version__, "sources": ", ".join(sources)}

    md_path, json_path = write_reports(findings, args.out, meta)

    print(f"Events loaded : {len(events)}")
    print(f"Sources       : {', '.join(sources)}")
    print(f"Findings      : {len(findings)}")
    print(f"Markdown      : {md_path}")
    print(f"JSON          : {json_path}")

    if args.stdout:
        print("\n" + render_markdown(findings, meta))

    has_blocking = any(f.severity.value in ("critical", "high") for f in findings)
    return 2 if has_blocking else 0


if __name__ == "__main__":
    sys.exit(main())