import { defineConfig } from '@playwright/test'

// This suite drives the real app end to end (register → login → generate →
// project), so it needs the full stack (frontend + backend + Postgres +
// Redis) already running — start it with `docker compose up --build` from
// the repo root, then run `npm run test:e2e` from `frontend/`. There is no
// `webServer` here on purpose: `npm run dev` alone can't provide a working
// backend/database for this flow to exercise.
export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30_000,
  fullyParallel: false,
  retries: 0,
  // The target is Vite's (unbundled, many-small-requests) dev server rather
  // than a production build, so the default 5s assertion timeout is tight.
  expect: { timeout: 10_000 },
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    trace: 'retain-on-failure',
  },
})
