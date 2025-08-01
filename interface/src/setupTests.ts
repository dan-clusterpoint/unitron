import { afterAll, afterEach, beforeAll } from 'vitest'
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
    }),
  ),
  http.post('/insight', () =>
    Response.json({ markdown: 'Test insight', degraded: false }),
  ),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

