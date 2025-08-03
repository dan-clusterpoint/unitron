export const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

if (!BASE_URL && import.meta.env.MODE !== 'test') {
  console.warn('API base URL not configured \u2013 check `.env`')
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
