# Public dashboard data contract

The dashboard is static GitHub Pages. Only sanitized, non-secret, non-personal, research-only data may be published in `data/status.json`.

The initial status file is deliberately explicit that market feeds and forward-test portfolios are **not connected**. `updated_at: null` means no market observation has been ingested. `starting_cash_gbp` is a proposed virtual allocation, not actual portfolio equity.

Future automation must publish only after validating schema, timestamp, quote currency, data source, staleness, and completeness. Never publish xAI credentials, broker tokens, private holdings, wallet addresses, private research files, or unverified P&L. Publishing requires a separate authenticated write workflow from the private engine, with least-privilege access and a tested rollback path.
