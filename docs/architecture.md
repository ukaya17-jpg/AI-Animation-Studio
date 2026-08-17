# Architecture

## Backend boundaries

`api` is the HTTP boundary and contains routes, middleware, dependencies, and exception handlers. It delegates work to `services`; routes do not query databases or call AI providers directly.

`core` contains configuration, logging, request context, rate-limit contracts, and shared exceptions. `database` owns SQLAlchemy and Redis client lifecycle. `models` and `repositories` now hold Sprint 2/3 persistence (`User`, `Project`, `GeneratedEpisode` and their repositories); provider integrations still belong in `adapters` and `providers`, both still empty.

The `events`, `tasks`, `workers`, `cache`, `media`, `storage`, `prompts`, `adapters`, `providers`, and `telemetry` namespaces are reserved integration boundaries and remain intentionally empty, so later work has explicit dependency directions without speculative implementation. (`app/services/prompt_generator.py` is a Sprint 3 service that builds prompt text for the deterministic episode generator; it does not use the reserved `prompts` boundary, which is for a future templating/versioning layer.)

## Request lifecycle

1. Trusted-host and optional HTTPS middleware validate the request boundary.
2. A request ID is created or propagated and attached to structured logs and the response.
3. The rate-limit hook runs before routes. It is still a no-op (`NoopRateLimiter`); a Redis-backed policy remains unscheduled.
4. Routes resolve services through dependency injection; `get_current_user` (added in Sprint 2) resolves a bearer JWT into a `User` for endpoints that require authentication.
5. Lifespan shutdown disposes SQLAlchemy connections and Redis clients.

## Sprint status

- **Sprint 2 — done.** `POST /auth/register` and `POST /auth/login` issue bcrypt-hashed accounts and JWT bearer access tokens; `POST/GET /projects` are scoped to the authenticated owner via `get_current_user`. Migrations: `2d5160e78e57` (users, projects).
- **Sprint 3 — in progress.** The Neşeli Orman module (`app/services/episode_generator.py`, `episode_seo.py`, `episode_shorts.py`, `content_bank.py`) deterministically generates episodes, SEO packages, and Shorts plans from a fixed content bank (no external AI call yet), persists them (`GeneratedEpisode`, optionally linked to a `Project` via `project_id`), and exposes them under `/episodes`. Real external AI provider adapters and an asynchronous job queue — the `adapters`/`providers`/`tasks`/`workers` boundaries — are still unimplemented; see [the Veo/fal.ai research note](veo-fal-ai-research.md) for the planned provider.

## Frontend

React Router owns navigation; the sidebar nav collapses into a horizontal scrollable bar below the `md` breakpoint so the layout stays usable at mobile widths (375px and up). `src/lib/api.ts` is the shared Axios boundary for future API calls. The application has a root error boundary, responsive dark-ready layout, and a reusable loading state (`role="status"`) used consistently across every network call on `/episodes`.

## Deployment

Development uses Docker Compose with PostgreSQL and Redis health checks. Production must set a unique `APP_SECRET_KEY`, secure database credentials, explicit CORS/trusted-host lists, and `FORCE_HTTPS=true`.
