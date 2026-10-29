> **Work in progress:** Not ready for customer data or a paid pilot. See `docs/BASELINE_AUDIT.md` and `SERVICE_CONTRACT.md`. Existing sales materials contain unvalidated claims.

# Conversion-Tracking Integrity Audit

Reusable engine + demonstration for diagnosing purchase / conversion tracking problems across Shopify, GA4, and Google Ads.

**Commercial offer:** $500 fixed-price diagnostic (see original opportunity brief).

## What it finds

- Duplicate purchase events (same transaction ID multiple times)
- Missing transactions (present in one source, absent in another)
- Revenue value mismatches for the same order
- Consent-related gaps when the field is present
- Source coverage summary

## Quick start (demo)

```bash
python demo.py
```

Runs against synthetic data that intentionally contains:
- 3 duplicate purchases
- 2 incorrect values
- 1 missing conversion

## Audit real exports

```bash
python -m engine.runner sample_data/shopify_orders.csv sample_data/ga4_purchases.csv sample_data/google_ads_conversions.csv --out reports/ --stdout
```

Accepts one or more CSV/JSON files. Column names are matched flexibly (`transaction_id` / `order_id`, `value` / `revenue`, etc.).

## Client materials

- `CLIENT_INSTRUCTIONS.md` — one-page instructions to send clients
- `docs/service.html` — website service advertisement page (update the CTA email before publishing)

## Project layout

```
conversion-tracking-audit/
├── demo.py
├── engine/
│   ├── loader.py
│   ├── checks.py
│   ├── reporter.py
│   └── runner.py
├── sample_data/          # Synthetic Shopify + GA4 + Google Ads exports
├── docs/service.html
├── CLIENT_INSTRUCTIONS.md
└── requirements.txt
```

## Stack

- Python, CSV/JSON only
- No paid APIs or browser automation required for the core audit
- Live GA4 DebugView / GTM Preview can be used as optional manual validation

## Commercial notes

Build the discrepancy report and synthetic demo first. Do not promise deep live diagnostics until GA4/GTM competence is validated on real accounts. Reject open-ended analytics troubleshooting inside the $500 fee.