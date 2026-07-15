# Deployment

Quill is two deployables that must be hosted separately:

| Part | Where it can run | Why |
| --- | --- | --- |
| **Next.js frontend** (`frontend/`) | **Vercel** (or any Node host) | Standard Next.js 14 App Router app. |
| **FastAPI backend** (`app/`, `main.py`) | **A container/VM host** — Render, Railway, Fly.io, a VPS | Long-running ASGI server with **WebSockets** (live notifications), a **PostgreSQL** database, and **persistent file uploads**. None of these fit Vercel's stateless serverless model, so the backend cannot run on Vercel. |

The frontend is non-functional until `API_URL` points at a reachable backend, so **deploy the backend first**, then wire its public URL into the frontend.

---

## 1. Backend → container host

The repo ships a `Dockerfile` (`uvicorn main:app` on port 8000) and a `docker-compose.yml` (app + Postgres 15). Any host that can build the Dockerfile and attach a Postgres database works.

**Required environment variables** (see `.env.example`):

| Var | Notes |
| --- | --- |
| `DATABASE_URL` | `postgresql://user:pass@host:5432/dbname` — provision a managed Postgres on the same host. |
| `SECRET_KEY` | ≥ 32 chars. The app fails fast if unset. |
| `ALLOWED_HOSTS` | Comma-separated trusted Host headers, e.g. `api.yourdomain.com`. |
| `FRONTEND_URL` | The deployed frontend origin, for CORS, e.g. `https://quill.vercel.app`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default `30`. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default `7`. |
| `UPLOAD_FOLDER` | Default `uploads`. **Must be a persistent volume** — uploads (covers, avatars) are written to disk and served from `/media`. On an ephemeral filesystem they vanish on redeploy; mount a volume or switch this to object storage. |

**Migrations:** run `alembic upgrade head` against `DATABASE_URL` on deploy (release/start command).

After deploy, note the public base URL, e.g. `https://quill-api.onrender.com`. Confirm `GET /health` returns `{"status":"ok"}`.

---

## 2. Frontend → Vercel

1. **Import the repo** in the Vercel dashboard.
2. Set **Root Directory = `frontend`** (the Next.js app lives in a subdirectory). Framework preset auto-detects as Next.js.
3. Set **Environment Variables** (see `frontend/.env.example`):

   | Var | Value |
   | --- | --- |
   | `API_URL` | The backend base URL from step 1, e.g. `https://quill-api.onrender.com`. Server-side; used by the API proxy and every server component. |
   | `SITE_URL` | The frontend's own public origin, e.g. `https://quill.vercel.app`. Drives OpenGraph/canonical URLs. |
   | `NEXT_PUBLIC_WS_URL` | *(optional)* WebSocket URL if the backend socket is on a different host, e.g. `wss://quill-api.onrender.com/ws/notifications`. |

4. **Deploy.** The frontend proxies `/api/*` and `/media/*` to `API_URL`, so no CORS config is needed browser-side.

---

## 3. Wire the two together

- Backend `FRONTEND_URL` → the Vercel origin.
- Frontend `API_URL` → the backend origin.
- Backend `ALLOWED_HOSTS` → include the backend's own hostname.

Redeploy whichever side you changed after setting these.
