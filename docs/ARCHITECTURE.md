# Architecture

Quill is a FastAPI backend and a Next.js frontend. The backend follows a
layered design so each concern has one home and dependencies point inward.

```
app/
├── main.py            # app factory: middleware + router registration (composition root)
├── core/
│   ├── config.py      # Settings — the single source of environment configuration
│   └── security.py    # password hashing, JWT/refresh/ws/preview token lifecycle
├── db/
│   ├── base_class.py  # declarative Base
│   ├── base.py        # imports all models → full metadata (create_all / Alembic)
│   └── session.py     # engine + get_db dependency
├── models/            # SQLAlchemy ORM tables (one file per aggregate)
├── schemas/           # Pydantic request/response contracts
├── services/          # domain logic (queries + rules), grouped by aggregate
├── api/
│   ├── deps.py        # request-scoped auth dependencies (the authz surface)
│   └── routes/        # thin HTTP routers — validate, call a service, shape response
├── utils/             # pure helpers: sanitize, text, file validation
└── ws.py              # in-process WebSocket connection registry
```

## Layer rules (dependencies point inward)

- **Routes** depend on **services**, **schemas**, and **deps** — never on the ORM
  session directly for business logic. A router validates input, calls a service,
  and maps the result to a schema.
- **Services** hold the domain logic and own database queries. They depend on
  **models** and **core**, never on FastAPI. This is what makes them unit-testable
  and reusable across routers.
- **core** and **db** depend on nothing above them. Configuration is read once into
  a `Settings` object; everything else imports from there.

## How the SOLID principles show up

- **Single responsibility** — `core.config` owns configuration, `core.security`
  owns tokens, each `services/*` module owns one aggregate's rules, each router owns
  one resource's HTTP surface. Changing "how search works" touches one service
  function, not a 400-line grab-bag.
- **Open/closed** — `main.py` builds the app from a `ROUTERS` table; adding a
  feature area means appending a router and a service module, not editing existing
  wiring. New notification types plug into a lookup map rather than a chain of `if`s.
- **Liskov** — the auth dependencies return the same `UserDB` contract whether the
  caller needs any user, an admin, or a super admin; routes can depend on the
  narrowest one without special-casing.
- **Interface segregation** — routers pick the exact dependency they need
  (`get_current_user`, `get_optional_user`, `require_admin`, `require_super_admin`)
  instead of one god-dependency with flags.
- **Dependency inversion** — routers depend on the service *abstraction* (a stable
  function surface re-exported from `services/__init__.py`), not on concrete query
  code. Swapping an implementation leaves callers untouched.

## Request lifecycle

1. Middleware runs (CORS → security headers → rate limit → trusted host).
2. The route's dependencies resolve: `get_db` opens a session; an auth dependency
   validates the token and loads the user.
3. The route calls one or more service functions.
4. The response is serialized through a Pydantic schema (`from_attributes`).
5. `get_db` closes the session; `HTTPException`s pass through as control flow.

See `docs/PRODUCT.md` for the feature catalog.
