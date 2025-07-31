import { useState } from 'react'
import { marked } from 'marked'
import type { ParsedInsight, Action } from '../utils/insightParser'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from './ui/card'
import { Badge } from './ui/badge'
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from './ui/accordion'
import Sheet from './ui/sheet'
import { downloadBase64 } from '../utils'

function actionsToMarkdown(actions: Action[]): string {
  return actions
    .map((a, i) => {
      const lines = [`### ${i + 1}. ${a.title}`]
      if (a.reasoning) lines.push(a.reasoning)
      if (a.benefit) lines.push(`**Benefit:** ${a.benefit}`)
      return lines.join('\n')
    })
    .join('\n\n')
}

export interface InsightCardProps {
  insight: ParsedInsight
  loading?: boolean
}

export default function InsightCard({ insight, loading = false }: InsightCardProps) {
  const { evidence, actions, personas } = insight
  const [copied, setCopied] = useState(false)
  const [open, setOpen] = useState(false)
  const safeActions = Array.isArray(actions) ? actions : []
  const safePersonas = Array.isArray(personas) ? personas : []
  const markdown = actionsToMarkdown(safeActions)
  const html = marked.parse(markdown)

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(markdown)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // ignore clipboard errors
    }
  }

  function onDownload() {
    const encoded = typeof btoa === 'function'
      ? btoa(markdown)
      : Buffer.from(markdown, 'utf-8').toString('base64')
    downloadBase64(encoded, 'actions.md')
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

  const hasActions = safeActions.length > 0
  const hasPersonas = safePersonas.length > 0

  return (
    <Card className="space-y-4">
      {evidence && (
        <CardHeader>
          <CardTitle>Insight</CardTitle>
        </CardHeader>
      )}
      {evidence && (
        <CardContent>
          <p className="prose max-w-none">{evidence}</p>
        </CardContent>
      )}
      {hasActions ? (
        <CardContent>
          <Accordion
            type="multiple"
            defaultValue={safeActions.map((a) => a.id)}
            className="w-full"
          >
            {safeActions.map((a) => (
              <AccordionItem key={a.id} value={a.id}>
                <AccordionTrigger>{a.title}</AccordionTrigger>
                <AccordionContent>
                  {a.reasoning && <p>{a.reasoning}</p>}
                  {a.benefit && (
                    <Badge className="mt-2 inline-block">{a.benefit}</Badge>
                  )}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      ) : (
        <CardContent>
          No recommended actions were generated for this analysis.
        </CardContent>
      )}
      {hasPersonas ? (
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {safePersonas.map((p) => (
              <div key={p.id} className="flex items-start space-x-2 border rounded p-2">
                <img
                  src={`https://api.dicebear.com/7.x/identicon/svg?seed=${encodeURIComponent(
                    p.name || p.id,
                  )}`}
                  alt={p.name || p.id}
                  className="w-8 h-8 rounded-full"
                />
                <div className="space-y-1">
                  <div className="font-semibold">{p.name || p.id}</div>
                  {Object.entries(p)
                    .filter(([k]) => k !== 'id' && k !== 'name')
                    .map(([k, v]) => (
                      <div key={k} className="text-sm text-gray-600">
                        <span className="font-medium capitalize">{k}:</span>{' '}
                        {String(v)}
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      ) : (
        <CardContent>No data</CardContent>
      )}
      {hasActions && (
        <CardContent className="flex gap-2">
          <button className="btn-primary text-sm" onClick={copyToClipboard}>
            {copied ? 'Copied' : 'Copy Actions'}
          </button>
          <button className="btn-primary text-sm" onClick={() => setOpen(true)}>
            View Markdown
          </button>
        </CardContent>
      )}
      <Sheet open={open} onClose={() => setOpen(false)}>
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: html }}
        />
        <button className="btn-primary mt-4" onClick={onDownload}>
          Download Markdown
        </button>
      </Sheet>
    </Card>
  )
}
