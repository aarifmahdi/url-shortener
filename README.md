# URL Shortener

A backend URL shortener REST API built with FastAPI, PostgreSQL, and async SQLAlchemy — built as a
portfolio project, with real architectural decisions documented
in [DECISIONS.md](./DECISIONS.md).

## Status
v1 backend completed.

**Done:**
- Project structure, schema, and short-code strategy designed and documented
- PostgreSQL database configured
- Async architecture decided (FastAPI + asyncpg + async SQLAlchemy)
- `database.py` and `models.py`
- base62 encoding and `crud.py` implementation
- Core endpoints: create short URL, redirect

**Next:**
- SQA Testing 
- Simple frontend (submit long URL, display short URL)
- Deployment (Docker, CI/CD, cloud hosting)

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

1. Clone the repo and create a virtual environment:
```bash
   git clone https://github.com/aarifmahdi/url-shortener.git
   cd url-shortener
   python -m venv venv
   venv\Scripts\activate       # Windows
```

2. Install dependencies:
```bash
   pip install -r requirements.txt
```

3. Set up PostgreSQL and create a database (e.g. `url_shortener_db`).

4. Copy `.env.example` to `.env` and fill in your values:
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=url_shortener_db
BASE_URL=http://localhost:8000


5. Run database migrations:
```bash
   alembic upgrade head
```

6. Start the server (must be run from the project root):
```bash
   uvicorn app.main:app --reload
```

7. Open `http://localhost:8000/docs` to try the API interactively.