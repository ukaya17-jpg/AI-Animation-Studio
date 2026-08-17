import { defineConfig } from '@playwright/test'

// This suite drives the real app end to end (register → login → generate →
// project), so it needs the full stack (frontend + backend + Postgres +
// Redis) already running — start it with `docker compose up --build` from
// the repo root, then run `npm run test:e2e` from `frontend/`. There is no
// `webServer` here on purpose: `npm run dev` alone can't provide a working
// backend/database for this flow to exercise.
export default defineConfig({
  testDir: './tests/e2e',
  // Generous relative to a typical CI runner: the target is Vite's dev
  // server (unbundled, many small requests) plus a full register → generate
  // → save → verify flow across several real network round trips.
  timeout: 60_000,
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  expect: { timeout: 20_000 },
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    trace: 'retain-on-failure',
  },
})
