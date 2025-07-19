import { test, expect } from "vitest"
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import App from './App'

// mock fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ domain: 'example.com' }),
  } as Response)
) as any

test('renders input and calls fetch', async () => {
  global.IntersectionObserver = vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn(),
  })) as unknown as typeof IntersectionObserver
  render(<App />)
  const input = screen.getByPlaceholderText('https://example.com')
  await userEvent.type(input, 'https://example.com')
  userEvent.click(screen.getByRole('button', { name: /analyze/i }))
  await waitFor(() => expect(fetch).toHaveBeenCalled())
  await screen.findByText(/couldn’t find any insights/i)
})
