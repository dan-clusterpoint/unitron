import { marked } from 'marked'
import { Card, CardContent } from './ui/card'
import { useState } from 'react'

export interface InsightCardProps {
  markdown: string
  loading?: boolean
}

export default function InsightCard({ markdown, loading = false }: InsightCardProps) {
  const [copied, setCopied] = useState(false)

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* ignore */
    }
  }

  if (loading) {
    return (
      <Card className="p-4" data-testid="insight-skeleton">
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-4 bg-gray-200 rounded" />
          <div className="h-4 bg-gray-200 rounded w-5/6" />
        </div>
      </Card>
    )
  }

  const content = markdown.trim()
    ? <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: marked.parse(markdown) }} />
    : <p>Analysis unavailable</p>

  return (
    <Card className="space-y-4">
      <CardContent>{content}</CardContent>
      {markdown.trim() && (
        <CardContent className="flex gap-2">
          <button className="btn-primary text-sm" onClick={copyToClipboard}>
            {copied ? 'Copied' : 'Copy Markdown'}
          </button>
        </CardContent>
      )}
    </Card>
  )
}
