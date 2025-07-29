import type { ParsedInsight } from '../utils/insightParser'
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

export interface InsightCardProps {
  insight: ParsedInsight
}

export default function InsightCard({ insight }: InsightCardProps) {
  const { evidence, actions, personas } = insight
  return (
    <Card className="space-y-4">
      {evidence && (
        <CardHeader>
          <CardTitle>Insight</CardTitle>
        </CardHeader>
      )}
      {evidence && (
        <CardContent>
          <div className="prose max-w-none">
            <p>{evidence}</p>
          </div>
        </CardContent>
      )}
      {actions.length > 0 && (
        <CardContent>
          <Accordion
            type="multiple"
            defaultValue={actions.map((a) => a.id)}
            className="w-full"
          >
            {actions.map((a) => (
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
      )}
      {personas.length > 0 && (
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {personas.map((p) => (
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
      )}
    </Card>
  )
}
