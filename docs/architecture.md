# Architecture

## Backend boundaries

`api` is the HTTP boundary and contains routes, middleware, dependencies, and exception handlers. It delegates work to `services`; routes do not query databases or call AI providers directly.

`core` contains configuration, logging, request context, rate-limit contracts, and shared exceptions. `database` owns SQLAlchemy and Redis client lifecycle. Future persistence belongs in `models` and `repositories`; provider integrations belong in `adapters` and `providers`.

The `events`, `tasks`, `workers`, `cache`, `media`, `storage`, `prompts`, and `telemetry` namespaces are reserved integration boundaries. They are intentionally empty in Sprint 1 so later work has explicit dependency directions without speculative implementation.

## Request lifecycle

1. Trusted-host and optional HTTPS middleware validate the request boundary.
2. A request ID is created or propagated and attached to structured logs and the response.
3. The rate-limit hook runs before routes. It is a no-op until Sprint 2 configures a Redis-backed policy.
4. Routes resolve services through dependency injection.
5. Lifespan shutdown disposes SQLAlchemy connections and Redis clients.

## Frontend

React Router owns navigation. `src/lib/api.ts` is the shared Axios boundary for future API calls. The application has a root error boundary, responsive dark-ready layout, and a reusable loading state.

## Deployment

Development uses Docker Compose with PostgreSQL and Redis health checks. Production must set a unique `APP_SECRET_KEY`, secure database credentials, explicit CORS/trusted-host lists, and `FORCE_HTTPS=true`.
