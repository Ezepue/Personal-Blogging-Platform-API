# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database
```bash
alembic upgrade head          # Apply migrations
alembic revision --autogenerate -m "description"  # Generate new migration
alembic downgrade -1          # Rollback one migration
```

### Run Server
```bash
uvicorn main:app --reload     # Development with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000  # Production
```

### Docker
```bash
docker-compose up -d          # Start all services (API + PostgreSQL)
docker-compose down           # Stop services
```

### API Docs
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Environment Variables

Required in `.env`:
```
DATABASE_URL=postgresql://username:password@localhost:5432/blog_db
SECRET_KEY=your-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
UPLOAD_FOLDER=uploads
```

`DATABASE_URL` and `SECRET_KEY` are mandatory — the app will not start without them. `config.py` validates token expiry ranges (1–1440 min for access, 1–365 days for refresh).

## Architecture

### Layer Overview

```
routes/        → HTTP handlers, request validation via Pydantic schemas
utils/         → Business logic (auth_helpers.py, db_helpers.py, notification_helper.py)
models/        → SQLAlchemy ORM models
schemas/       → Pydantic request/response shapes
database.py    → Engine + SessionLocal + get_db() dependency
config.py      → Env var loading and validation
main.py        → App creation, router registration, middleware
```

### Authentication Flow

- JWT access tokens (HS256, 30 min default) + refresh tokens (7 days, stored in DB)
- `utils/auth_helpers.py` handles: password hashing (bcrypt), token creation/verification, role checking
- `routes/users.py` handles: register, login (rate-limited 3/min), logout, refresh
- Refresh tokens are tracked in the `refresh_tokens` table with revocation support

### Role-Based Access Control

Four roles defined in `models/enums.py`: `READER`, `AUTHOR`, `ADMIN`, `SUPER_ADMIN`

Role checks are enforced in route handlers via helper functions in `utils/auth_helpers.py`. Only `SUPER_ADMIN` can delete users or create other admins.

### Database Patterns

- All sessions use the `get_db()` dependency injected via `Depends(get_db)`
- Connection pool: 10 persistent connections, 20 max overflow (`database.py`)
- `tags` field on articles uses JSONB
- Comments use soft-delete (`is_deleted` flag) rather than hard delete
- Likes have a unique constraint on `(user_id, article_id)`
- Cascading deletes are configured on relationships (delete user → delete their articles, comments, etc.)

### WebSocket

`websocket_manager.py` manages per-user WebSocket connections for real-time notifications. The notification system is partially implemented (routes in `routes/notifications.py`).

### Frontend

Static HTML/CSS/JS lives in `frontend/`. The FastAPI app serves these directly. The frontend uses `frontend/api/` utilities to communicate with the backend.
