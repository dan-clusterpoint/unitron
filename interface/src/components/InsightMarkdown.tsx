import MarkdownPreview from '@uiw/react-markdown-preview'
import DOMPurify from 'dompurify'
import { Card, CardContent } from './ui/card'

export interface InsightMarkdownProps {
  markdown: string
  loading?: boolean
  degraded?: boolean
}

export default function InsightMarkdown({ markdown, loading = false, degraded = false }: InsightMarkdownProps) {
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

  const sanitized = DOMPurify.sanitize(markdown)
  const hasContent = sanitized.trim().length > 0

  const handleExport = () => {
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'insight.md'
    link.click()
    URL.revokeObjectURL(url)
  }

  const content = hasContent
    ? <MarkdownPreview source={sanitized} className="prose max-w-none" />
    : <p>Analysis unavailable</p>

  return (
    <Card className="space-y-4">
      {degraded && (
        <div className="border border-yellow-500 bg-yellow-50 text-yellow-700 p-2 rounded mb-2 text-sm">
          Partial results shown due to degraded analysis.
        </div>
      )}
      {hasContent && (
        <CardContent className="flex justify-end pt-0">
          <button onClick={handleExport} className="btn-primary">
            Export Markdown
          </button>
        </CardContent>
      )}
      <CardContent>{content}</CardContent>
    </Card>
  )
}
