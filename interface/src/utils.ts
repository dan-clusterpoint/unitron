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

export function downloadBase64(encoded: string, filename: string): void {
  try {
    const data = atob(encoded)
    const blob = new Blob([data], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 100)
  } catch {
    // ignore errors
  }
}
