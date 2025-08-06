import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import '@testing-library/jest-dom'
import { setupServer } from 'msw/node'
import { http } from 'msw'

const BASE = 'http://localhost:8080'

export const server = setupServer(
  http.get(`${BASE}/ready`, () => Response.json({ ready: true })),
  http.post(`${BASE}/snapshot`, () =>
    Response.json({
      snapshot: {
        profile: { name: 'Example Co' },
        digitalScore: 0,
        stackDelta: [],
        growthTriggers: [],
        nextActions: [],
      },
    }),
  ),
  http.post(`${BASE}/insight`, () =>
    Response.json({ markdown: 'Test insight', degraded: false }),
  ),
)

vi.stubEnv('VITE_API_BASE_URL', BASE)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

