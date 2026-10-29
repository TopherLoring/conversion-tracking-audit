> **Historical draft:** Not approved for client use. See `SERVICE_CONTRACT.md` and `docs/BASELINE_AUDIT.md`.

# Conversion-Tracking Integrity Audit — Client Instructions

**What this is**  
A fixed-scope diagnostic of your purchase / conversion tracking across Shopify (or similar), Google Analytics 4, and Google Ads. We identify duplicate events, missing transactions, revenue value mismatches, and related attribution problems that distort campaign decisions.

**Price**  
$500 fixed (typical). Confirmed after a quick review of the data you provide.

---

### What you need to send

1. **Event exports (required)**  
   Provide purchase/conversion data from the systems you use. Preferred formats:

   - **Shopify**: Orders export (CSV) for a recent 7–30 day window, or order list with order name/ID + total.
   - **GA4**: Purchase events export or Exploration (transaction ID, value, timestamp). CSV or Google Sheets OK.
   - **Google Ads**: Conversion upload / conversion details that include transaction/order ID and value, if available.

   If you cannot export from one platform, screenshots of key conversion diagnostics plus a description of the setup are acceptable for scoping.

2. **One-sentence context**  
   Example: “We spend ~$8k/month on Google Ads for a Shopify store and GA4 purchase numbers never match Ads or Shopify.”

3. **Access (optional)**  
   Read-only access to GA4, Google Ads, and GTM can speed diagnosis but is **not required** for the core audit if you can provide the exports above.

4. **Redaction**  
   Remove customer PII (names, emails, addresses) if possible. Order IDs and revenue figures are needed.

---

### What you will receive

- Prioritized findings report (duplicates, missing purchases, value mismatches, consent signals)
- Clear evidence tied to specific transaction IDs
- Concrete fix recommendations (tag/GTM/Consent Mode / data-layer level)
- Short walkthrough (Loom or call)
- Optional separate quote for implementation

---

### Process & timeline

| Step | What happens | Typical time |
|------|--------------|--------------|
| 1 | You send exports + context | — |
| 2 | Scope check & firm confirmation | Same day |
| 3 | Audit + report | 1–2 business days |
| 4 | Walkthrough delivered | Included |

Active diagnostic time is normally 2–3 hours.

---

### In scope

- Comparison of purchase events across the sources you provide
- Detection of duplicate events, missing transactions, and value mismatches
- High-level consent / attribution observations when data supports it
- Actionable recommendations

### Out of scope

- Full media buying or campaign optimization
- Ongoing tracking maintenance retainers
- Server-side GTM / CAPI full builds (available separately)
- Formal privacy/legal compliance certification

---

### How to get started

Reply with:

1. The event export files (or secure share link)
2. The one-sentence context
3. Any known discrepancies you already see

You will receive confirmation of scope and price before work begins.

---

*Questions? Just reply.*  
*This is a diagnostic service. Implementation of fixes is quoted separately.*