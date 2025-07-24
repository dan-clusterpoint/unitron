export type Martech = Partial<{
  core: string[]
  adjacent: string[]
  broader: string[]
  competitors: string[]
}>

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

export default function MartechResults({ martech }: { martech: Martech }) {
  const buckets: (keyof Martech)[] = ['core', 'adjacent', 'broader', 'competitors']
  const hasAny = buckets.some((b) => martech[b] && martech[b]!.length > 0)
  return (
    <div className="bg-gray-50 p-4 rounded">
      <h3 className="font-medium mb-2">Martech Vendors</h3>
      {hasAny ? (
        buckets.map((bucket) => (
          <div key={bucket} className="mb-2">
            <h4 className="font-medium capitalize">{bucket}</h4>
            {renderList(martech[bucket] || [])}
          </div>
        ))
      ) : (
        <p className="italic">Nothing detected</p>
      )}
    </div>
  )
}
