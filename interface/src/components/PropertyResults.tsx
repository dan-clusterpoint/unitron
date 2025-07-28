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
      {items.map((i, idx) => (
        <li key={i}>
          {i}{' '}
          <sup id={`fnref${idx + 1}`}>
            <a
              href={`#fn${idx + 1}`}
              className="underline text-blue-800 focus:outline-none focus:ring-2 ring-offset-2 ring-blue-500"
              tabIndex={0}
            >
              [{idx + 1}]
            </a>
          </sup>
        </li>
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
