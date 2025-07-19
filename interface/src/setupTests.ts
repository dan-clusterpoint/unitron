import { afterAll, afterEach, beforeAll } from 'vitest'
import '@testing-library/jest-dom'
import { setupServer } from 'msw/node'
import { http } from 'msw'

export const server = setupServer(
  http.get('/ready', () => Response.json({ ready: true })),
  http.post('/analyze', () =>
    Response.json({ domain: 'example.com', martech: { core: [] } }),
  ),
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

