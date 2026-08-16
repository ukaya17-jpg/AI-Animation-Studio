# Sprint 1 architecture audit

Audit date: 2026-07-28.

## Current state

The repository provides a FastAPI/React foundation with Docker Compose, PostgreSQL,
Redis, Alembic, and continuous integration. The backend boundary is appropriate for
the current scope: API routes delegate to services and infrastructure clients remain
outside routes.

## Prioritized findings

| Priority | Finding | Status |
| --- | --- | --- |
| Critical | No authentication, project model, migrations, AI providers, or rendering pipeline | Deferred: Sprint 2+ roadmap work |
| High | Health endpoint did not distinguish process liveness from dependency readiness | Resolved |
| High | Database and Redis clients were not released at shutdown | Resolved |
| High | Production could boot using the documented development database password | Resolved |
| High | No request correlation, trusted-host protection, or HTTPS production guard | Resolved |
| Medium | No structured JSON logging or centralized error taxonomy beyond infrastructure readiness | Resolved for Sprint 1 platform errors |
| Medium | Frontend routes are intentional Sprint 1 placeholders | Deferred |
| Low | `latest` frontend dependencies reduce build reproducibility | Resolved |

## Delivered hardening

- `GET /health` remains a dependency-free liveness endpoint and preserves its existing response.
- `GET /health/ready` verifies PostgreSQL and Redis and returns HTTP 503 when either is unavailable.
- Infrastructure clients close during application shutdown.
- Production configuration rejects debug mode, a wildcard CORS origin, and the default database password.
- All API responses receive baseline anti-sniffing, clickjacking, and referrer-policy headers.
- Structured logs include the request ID; responses also return `X-Request-ID`.
- Trusted-host validation, production HTTPS enforcement, safe unhandled-error responses, and a rate-limit extension point are configured.
- Database sessions roll back when downstream request handling fails.
- MyPy is part of local and continuous-integration quality checks.

## Verification

`npm run lint` and `npm run build` pass in `frontend`. Backend source compilation passes.
The checked-in virtual environment contains no project dependencies (including `pytest`,
`ruff`, and `mypy`), so those backend checks must be run after the documented development
installation step. Docker Compose validation also requires Docker to be available locally.
