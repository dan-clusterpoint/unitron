const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export function normalizeUrl(url: string): string {
  let cleaned = url.trim()
  if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(cleaned)) {
    cleaned = 'https://' + cleaned
  }
  try {
    const parsed = new URL(cleaned)
    const scheme = parsed.protocol
    const netloc = parsed.host.toLowerCase()
    const path = parsed.pathname.replace(/\/+$/, '')
    return `${scheme}//${netloc}${path}`
  } catch {
    return cleaned
  }
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
