# AI Animation Studio

AI Animation Studio is a scalable foundation for creating, managing, and delivering AI-assisted animation projects. Sprint 1 provides the development platform, clear service boundaries, and automated quality checks for future generation, rendering, and collaboration capabilities.

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

## Quality checks

```bash
cd backend && python -m ruff check . && python -m mypy app && python -m pytest
cd frontend && npm run lint && npm run build
```

## Roadmap

1. Sprint 1: foundation, health monitoring, and development workflows.
2. Sprint 2: authentication, users, projects, and migrations.
3. Sprint 3: AI adapters, prompts, and asynchronous jobs.
4. Sprint 4: asset storage, rendering, and project workspace.
5. Sprint 5: observability, access control, and production deployment.

## Architecture

The backend uses clean architecture boundaries: API routes delegate to services; services coordinate repositories and provider adapters; persistence and infrastructure concerns remain isolated. New features should preserve these dependency directions and use dependency injection at API boundaries.

See [the architecture guide](docs/architecture.md) and [the Sprint 1 audit](docs/sprint-1-audit.md) for the current scope, security posture, and deferred roadmap work.

## License

Distributed under the [MIT License](LICENSE).
