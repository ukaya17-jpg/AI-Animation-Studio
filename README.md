# AI Animation Studio

AI Animation Studio is a scalable foundation for creating, managing, and delivering AI-assisted animation projects. Sprint 1 provided the development platform, clear service boundaries, and automated quality checks. Sprint 2 added authentication, users, and projects. A deterministic episode-generation module ("Neşeli Orman") demonstrates the Sprint 3 shape end to end: 20 fixed Turkish-language themes, each generating a full episode script, YouTube SEO package, and Shorts cut, with cast/location reference art and persistent storage.

## Feature highlights

- **Neşeli Orman episode studio:** pick from 20 fixed themes (each pairing 2 of 5 recurring characters and 1 of 4 locations) and generate a 5-scene episode script, a YouTube SEO package (titles/description/tags/thumbnail), and a Shorts cut plan, all in one request. Every generation is persisted to PostgreSQL and browsable in a newest-first history list.
- **Character and location reference art:** every character and location carries a static reference image, shown in the theme picker, generation results, and history list, with meaningful alt text for screen readers.
- **Authentication and projects:** email/password registration and login (bcrypt-hashed passwords, JWT bearer access tokens), and a `Project` model so a user can eventually group episodes into channels. Generated episodes optionally attach to a project via `project_id`.
- **Accessible, responsive UI:** loading and error states on every network call, a mobile-safe layout down to 375px, and semantic ARIA roles (`radiogroup`, `status`, `aria-live`) where they matter.
- **Optional rate limiting:** a Redis-backed, fixed-window limiter (tight on `/auth/login`/`/auth/register`, looser elsewhere) is ready to go behind `RATE_LIMIT_ENABLED=true`; it stays off by default so local dev and CI never need a live Redis connection.

## Technology stack

- **Backend:** Python 3.12, FastAPI, async SQLAlchemy, Alembic, PostgreSQL, Redis
- **Frontend:** React, TypeScript (strict), Vite, Tailwind CSS, React Router, Axios
- **Platform:** Docker Compose and GitHub Actions

## Installation

Prerequisites: Python 3.12+, Node.js 20+, and Docker Desktop (recommended).

```bash
cp .env.example .env
cd backend && python -m venv .venv && .venv/bin/pip install -e '.[dev]'
cd ../frontend && npm install
```

Run the API with `cd backend && .venv/bin/uvicorn app.main:app --reload`; run the UI with `cd frontend && npm run dev`. Liveness is available at `http://localhost:8000/health`; dependency readiness is available at `http://localhost:8000/health/ready`.

## Docker

Copy `.env.example` to `.env`, choose a secure `POSTGRES_PASSWORD`, then run:

```bash
docker compose up --build
```

The command starts frontend, backend, PostgreSQL, and Redis. The frontend runs at `http://localhost:5173` and the API at `http://localhost:8000`.

## API endpoints

| Method & path | Description |
| --- | --- |
| `GET /health` | Dependency-free process liveness. |
| `GET /health/ready` | Verifies PostgreSQL and Redis; `503` if either is unavailable. |
| `POST /auth/register` | Create an account (`email`, `password`); returns the created user. |
| `POST /auth/login` | Exchange email/password for a JWT bearer access token. |
| `POST /projects` | Create a project owned by the authenticated user. Requires a bearer token. |
| `GET /projects` | List every project owned by the authenticated user. Requires a bearer token. |
| `GET /episodes/themes` | List all 20 fixed Neşeli Orman themes, with cast/location names and images. |
| `POST /episodes/generate` | Generate an episode (script, SEO, Shorts) for a theme id; optional `project_id`. |
| `GET /episodes` | Newest-first, paginated episode history (`page`, `page_size` ≤ 100, optional `project_id` filter). |
| `GET /episodes/{id}` | Full detail for one previously generated episode. |
| `DELETE /episodes/{id}` | Delete one previously generated episode. |
| `POST /storyboards` | Turn a script into an unsaved storyboard (scenes, timing, statistics). |
| `POST /storyboards/export/{format}` | Generate a storyboard and export it as portable text (`markdown`, `json`, or `yaml`). |

`POST /projects`, `GET /projects`, and any future user-scoped endpoint expect an `Authorization: Bearer <token>` header from `POST /auth/login`.

## Quality checks

```bash
cd backend && python -m ruff check . && python -m mypy app && python -m pytest
cd frontend && npm run lint && npm run build
```

## Roadmap

1. Sprint 1 — done: foundation, health monitoring, and development workflows.
2. Sprint 2 — done: authentication (JWT bearer tokens, bcrypt-hashed passwords), a `User` model, a `Project` model, and their migrations.
3. Sprint 3 — in progress: the Neşeli Orman module ships a deterministic, content-bank-driven episode/SEO/Shorts generator, persisted generated episodes optionally linked to a project, and a prompt generator (`app/services/prompt_generator.py`). Real external AI provider adapters (`app/adapters`, `app/providers` — see [the Veo/fal.ai research note](docs/veo-fal-ai-research.md)) and an asynchronous job queue are still pending.
4. Sprint 4: asset storage, rendering, and project workspace.
5. Sprint 5: observability, access control, and production deployment.

## Architecture

The backend uses clean architecture boundaries: API routes delegate to services; services coordinate repositories and provider adapters; persistence and infrastructure concerns remain isolated. New features should preserve these dependency directions and use dependency injection at API boundaries.

See [the architecture guide](docs/architecture.md) and [the Sprint 1 audit](docs/sprint-1-audit.md) for the current scope, security posture, and deferred roadmap work.

## License

Distributed under the [MIT License](LICENSE).
