import type { ParsedInsight } from '../utils/insightParser'

export interface InsightCardProps {
  insight: ParsedInsight
}

export default function InsightCard({ insight }: InsightCardProps) {
  const { evidence, actions, personas } = insight
  return (
    <div className="bg-white shadow rounded p-6 space-y-4">
      {evidence && (
        <div className="prose">
          <p>{evidence}</p>
        </div>
      )}
      {actions.length > 0 && (
        <section>
          <h3 className="font-medium mb-2">Actions</h3>
          <ul className="list-disc list-inside space-y-1">
            {actions.map((a) => (
              <li key={a.id} className="space-y-1">
                <div className="font-semibold">{a.title}</div>
                {a.reasoning && <div>{a.reasoning}</div>}
                {a.benefit && <div className="text-sm text-gray-600">{a.benefit}</div>}
              </li>
            ))}
          </ul>
        </section>
      )}
      {personas.length > 0 && (
        <section>
          <h3 className="font-medium mb-2">Personas</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {personas.map((p) => (
              <div key={p.id} className="border rounded p-2">
                <div className="font-semibold mb-1">{p.name || p.id}</div>
                {Object.entries(p)
                  .filter(([k]) => k !== 'id' && k !== 'name')
                  .map(([k, v]) => (
                    <div key={k} className="text-sm text-gray-600">
                      <span className="font-medium capitalize">{k}:</span>{' '}
                      {String(v)}
                    </div>
                  ))}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
