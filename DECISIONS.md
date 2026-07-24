# Decisions Log

## v1 Scope
- Core loop: user submits long URL → gets short URL → visiting short URL redirects to long URL.
- No auth, no analytics, no rate limiting in v1 — deliberately minimal.

## Entities
- Single entity for v1: URL mapping (short_code <-> long_url). No User entity yet (no auth).

## Endpoints
- POST /short-urls — creates a new short code for a submitted long URL.
- GET /{short_code} — redirects to the long URL. Chose flat path (not nested under /short-urls)
  because the product requirement is a short, clean redirect link — practicality over strict REST nesting.

## URL creation behavior
- Always creates a new row/short code, even for a duplicate long_url. No reuse-check in v1.
  Reason: reuse only makes sense scoped to a user (per-user duplicate links), which requires auth.
  Faking identity via IP/cookies before real auth was considered and rejected — adds complexity now
  to solve a problem auth will solve cleanly and correctly later.
  -> Future (Phase: Auth): add owner_id FK on URL model; add reuse-check in POST /short-urls scoped per user.
     GET /{short_code} unaffected — redirect logic is identity-agnostic.

## Schema (v1 URL mapping table)
- id: surrogate PK, auto-incrementing integer. Chosen over short_code as PK — short_code is
  business data (can legitimately change later, e.g. collisions or a future "custom alias" feature),
  and a PK referenced by future FK's (e.g. analytics clicks table) should never need to change.
- short_code: unique, indexed (free via unique constraint).
- long_url: VARCHAR(2048) — 2048 is the commonly cited de facto practical URL length ceiling.
  NOT NULL — app-level validation already prevents missing long_url, but DB-level constraint is
  a backup against bugs or future direct DB writes bypassing the app.
- created_at: timestamp, set at row creation. Generically useful (debugging, ordering), not tied
  to any specific future feature. Cheap to add now, costly to backfill later.
- Alembic will handle future migrations (e.g. adding owner_id in Phase: Auth) without needing to
  recreate the table from scratch.

## Short-code generation strategy
- Fixed length of 4 characters (not growing-length). Base62 alphabet (a-z, A-Z, 0-9) → 62^4 ≈ 14.7M
  combinations — not a real constraint for a portfolio project.
- Chosen approach: deterministically base62-encode the row's `id` (Option B), not random generation
  with collision-retry (Option A). Since `id` is already guaranteed unique by the DB, this produces
  zero collision risk by construction — no retry logic needed at all.
- Base62 chosen over base16/base36 (less compact — fewer symbols per character) and base64
  (more compact, but includes `+` and `/`, which are not URL-safe and can break path parsing or
  get misinterpreted in query strings).

## Project structure (locked for v1)
```
url_shortener/
├── app/
│   ├── main.py            # creates FastAPI() app, includes routers — thin assembler only
│   ├── database.py        # engine + session factory + get_db dependency
│   ├── models.py           # SQLAlchemy ORM models (e.g. class URLMapper)
│   ├── schemas.py           # Pydantic request/response models (e.g. URLIn, URLOut)
│   ├── crud.py              # DB access functions (create_url_mapping, get_url_by_code, etc.)
│   └── routers/
│       └── url_routes.py    # APIRouter with the 2 v1 endpoints
├── requirements.txt
└── README.md
```
- models.py = SQLAlchemy (DB shape) vs schemas.py = Pydantic (API request/response shape) —
  standard convention across FastAPI codebases, avoids ambiguity of the word "model."
- routers/ (plural) anticipates future route files by topic (e.g. auth_routes.py in Phase: Auth),
  enabled by FastAPI's APIRouter — routes defined independently of `app`, then wired in via
  app.include_router() in main.py.
- crud.py functions currently double as our "business logic" since v1 logic is simple (no rules
  beyond straightforward create/read). A separate service.py layer is a later-phase concern, only
  worth introducing once logic sits above simple CRUD (e.g. ownership checks in Phase: Auth).

## Frontend note (new)
- I will build a simple frontend page (input long URL, receive/display short URL) — first FE
  usage in this project. Not yet designed; v1 backend still returns JSON, frontend is a separate
  future consumer of the API, not server-rendered HTML/templates.

  ## Database choice: PostgreSQL over SQLite
- SQLite locks the entire database file on writes; PostgreSQL uses row-level locking and
  supports many concurrent connections. For v1's traffic this alone isn't decisive, but it
  matters once analytics logging is added (see below).
- PostgreSQL runs as its own standalone service, separate from the FastAPI app process. This
  means other programs (analytics scripts, admin tools, future rate-limiting logic) can connect
  to and interact with the same database independently of the app — something a single-file
  SQLite database doesn't support as cleanly.
- Correction made during reasoning: initially assumed the GET /{short_code} redirect alone would
  bump into SQLite's write lock. That's wrong — a redirect lookup is a read, and reads don't
  trigger write locks. The real pressure comes from the future analytics phase.

-> Future (Phase: Analytics): once click-logging is added, each redirect becomes a read + write
   (look up short code, then log the hit). This is where SQLite's whole-file write lock would
   become a real bottleneck under load — the actual justification for choosing Postgres now,
   even though v1 traffic doesn't strictly require it yet.

## Async architecture: async def + asyncpg + async SQLAlchemy
- Chose async throughout (routes, driver, ORM session) since this app is I/O-bound — most work
  is waiting on DB round trips, not CPU computation.
- Correction made during reasoning: async does NOT make a single request faster. It doesn't speed
  up any individual operation — a single request takes roughly the same time whether async or sync.
  The actual benefit is throughput under concurrent load: while one request is waiting on I/O
  (e.g. a DB call), the event loop can process other requests instead of sitting idle. This is
  concurrency (interleaved work on one thread/process), not parallelism (simultaneous execution
  across CPU cores) — those are different things.
- Driver: async requires an async-native driver end-to-end. Using a sync driver (e.g. psycopg2)
  inside async def routes would silently block the whole event loop during DB calls, defeating
  the purpose. Chose asyncpg (async-native) + SQLAlchemy's async mode (AsyncSession,
  create_async_engine) to keep every layer of the chain async — the weakest sync link blocks
  everything, so consistency matters more than any single layer being async.
- Correct framing for interviews: "chosen because the app is I/O-bound, and async improves
  throughput under concurrent load — not the speed of any single request."

-> Future (Phase: Deployment/Scale): a single async server instance is not how apps like
   Netflix/Instagram/Uber handle millions of users. That requires horizontal scaling — many
   server instances behind a load balancer, each handling a manageable slice of traffic — plus
   database-side scaling (read replicas, sharding) and caching layers (Redis, CDNs). Async is a
   per-instance efficiency technique; horizontal scaling is the separate mechanism that gets you
   from "handles hundreds well" to "handles millions." Not needed for v1, but good to know exists.
-> Future (Phase: Auth): statelessness matters here — no server instance should hold user-specific
   data in its own memory between requests (so any instance can serve any user's next request).
   Session/login state should live in the DB or be carried by the client itself (e.g. JWT), not
   in server memory. The app is naturally stateless right now since nothing is stored outside
   Postgres; keep it that way when auth is added.