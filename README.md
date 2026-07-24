# URL Shortener

A backend URL shortener REST API built with FastAPI, PostgreSQL, and async SQLAlchemy — built as a
portfolio project, with real architectural decisions documented
in [DECISIONS.md](./DECISIONS.md).

## Status
🚧 In progress — backend setup phase.

**Done:**
- Project structure, schema, and short-code strategy designed and documented
- PostgreSQL database configured
- Async architecture decided (FastAPI + asyncpg + async SQLAlchemy)

**Next:**
- `database.py`, `models.py`, `crud.py` implementation
- Core endpoints: create short URL, redirect
- Simple frontend (submit long URL, display short URL)

**Planned (future phases):** authentication, click analytics, rate limiting.

## Tech Stack
- **Backend:** FastAPI (async)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy 2.0 (async)
- **Driver:** asyncpg

## Architecture (v1)
- Single entity: URL mapping (`short_code` ↔ `long_url`)
- `POST /short-urls` — creates a new short code for a submitted long URL
- `GET /{short_code}` — redirects to the original long URL
- Short codes are base62-encoded from the row's auto-incrementing `id` — deterministic,
  collision-free by construction (no random generation/retry logic needed)

See [DECISIONS.md](./DECISIONS.md) for full reasoning behind schema, database choice, and
async architecture.

## How to Run Locally
> ⚠️ Setup instructions coming once the core endpoints are implemented.