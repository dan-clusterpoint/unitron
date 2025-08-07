import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import '@testing-library/jest-dom'
import { setupServer } from 'msw/node'
import { http } from 'msw'

export const server = setupServer(
  http.get('/ready', () => Response.json({ ready: true })),
  http.post('/analyze', () =>
    Response.json({
      property: {
        domains: ['example.com'],
        confidence: 1,
        notes: ['all good'],
      },
      martech: { core: ['GTM'] },
      snapshot: {
        profile: { name: 'Example' },
        digitalScore: 50,
        stack: [],
        growthTriggers: [],
      },
    }),
  ),
)

vi.stubEnv('VITE_API_BASE_URL', '')

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

