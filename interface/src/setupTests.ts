import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import '@testing-library/jest-dom'
import { setupServer } from 'msw/node'
import { http } from 'msw'

export const server = setupServer(
  http.get('/ready', () => Response.json({ ready: true })),
  http.post('/snapshot', () =>
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
  http.post('/insight', () =>
    Response.json({ markdown: 'Test insight', degraded: false }),
  ),
)

vi.stubEnv('VITE_API_BASE_URL', '')

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

