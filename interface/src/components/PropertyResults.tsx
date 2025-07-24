export type Property = {
  domains: string[]
  confidence: number
  notes: string[]
}

function renderList(items: string[]) {
  if (!items || items.length === 0) {
    return <p className="italic">Nothing detected</p>
  }
  return (
    <ul className="list-disc list-inside space-y-1">
      {items.map((i) => (
        <li key={i}>{i}</li>
      ))}
    </ul>
  )
}

export default function PropertyResults({ property }: { property: Property }) {
  return (
    <>
      <div className="bg-gray-50 p-4 rounded mb-4">
        <h3 className="font-medium">Domains</h3>
        {renderList(property.domains)}
      </div>
      <div className="bg-gray-50 p-4 rounded mb-4">
        <h3 className="font-medium">Confidence</h3>
        <p>{Math.round(property.confidence * 100)}%</p>
      </div>
      <div className="bg-gray-50 p-4 rounded mb-4">
        <h3 className="font-medium mb-2">Notes</h3>
        {renderList(property.notes)}
      </div>
    </>
  )
}
