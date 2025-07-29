import type { ParsedInsight, Persona } from '../utils/insightParser'

export interface InsightCardProps {
  insight: ParsedInsight
}

function findPersonaName(personas: Persona[], id?: string) {
  if (!id) return undefined
  const match = personas.find((p) => p.id === id)
  return match?.name || id
}

export default function InsightCard({ insight }: InsightCardProps) {
  const { summary, actions, personas } = insight
  return (
    <div className="bg-white shadow rounded p-6 space-y-4">
      {summary && (
        <div className="prose">
          <p>{summary}</p>
        </div>
      )}
      {actions.length > 0 && (
        <section>
          <h3 className="font-medium mb-2">Actions</h3>
          <ul className="list-disc list-inside space-y-1">
            {actions.map((a, i) => (
              <li key={i} className="space-y-1">
                <div>
                  {a.persona && (
                    <span className="font-semibold mr-1">
                      {findPersonaName(personas, a.persona)}:
                    </span>
                  )}
                  {a.description}
                </div>
                {Array.isArray(a.evidence) && (
                  <ul className="list-disc list-inside ml-6">
                    {(a.evidence as unknown[]).map((e, idx) => (
                      <li key={idx}>{String(e)}</li>
                    ))}
                  </ul>
                )}
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
