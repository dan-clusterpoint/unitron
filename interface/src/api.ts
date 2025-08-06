const envBase = import.meta.env.VITE_API_BASE_URL
// Fall back to the gateway on port 8080 so requests don't hit the static server.
const fallback =
  typeof window !== 'undefined'
    ? `${window.location.protocol}//${window.location.hostname}:8080`
    : ''

export const BASE_URL = envBase || fallback

if (!envBase && import.meta.env.MODE !== 'test') {
  console.warn('API base URL not configured – check `.env`')
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE_URL + path, init)
  if (!res.ok) {
    let message: string
    try {
      message = await res.text()
    } catch {
      message = ''
    }
    throw new Error(message || `HTTP ${res.status}`)
  }
  try {
    return (await res.json()) as T
  } catch {
    throw new Error('Invalid response')
  }
}
