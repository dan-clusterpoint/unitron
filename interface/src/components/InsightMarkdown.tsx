import MarkdownPreview from '@uiw/react-markdown-preview'
import DOMPurify from 'dompurify'
import { Card, CardContent } from './ui/card'

export interface InsightMarkdownProps {
  markdown: string
  loading?: boolean
}

export default function InsightMarkdown({ markdown, loading = false }: InsightMarkdownProps) {
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

  const content = sanitized.trim()
    ? <MarkdownPreview source={sanitized} className="prose max-w-none" />
    : <p>Analysis unavailable</p>

  return (
    <Card className="space-y-4">
      <CardContent>{content}</CardContent>
    </Card>
  )
}
