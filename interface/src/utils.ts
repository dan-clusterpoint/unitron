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
