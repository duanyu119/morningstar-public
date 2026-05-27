# AGENTS.md

This is the entry file for automated coding agents working on MorningStar 启明星.

## Project Boundary

MorningStar is an open-source, local-first RSS/news collection toolkit. Version 0.1 focuses on public RSS feeds, JSON packets, and a small repeatable workflow.

Make the smallest change needed for the requested task. Do not refactor, rename, reformat, upgrade dependencies, or widen scope unless explicitly asked.

## Public Repository Rules

- Do not commit API keys, private RSS tokens, cookies, account IDs, database exports, generated digests, or local state.
- Keep runtime output under `data/`; it is ignored by git.
- Keep deployment artifacts, private app integrations, and personal review logs out of the public tree.
- Prefer example config files over real service credentials.

## Core Files

- `config/feeds.json` — public RSS source list for the v0.1 demo.
- `scripts/fetch_newsletter_items.py` — standalone fetcher.
- `README.md` — public bilingual project overview.
- `requirements.txt` — Python runtime dependencies.

## Verification

For changes to the fetcher, run:

```bash
python3 -m unittest
python3 scripts/fetch_newsletter_items.py --recent-per-feed 1 --include-seen --no-html
```

If network access is unavailable, run the unit tests and state clearly that live RSS fetching was not verified.
