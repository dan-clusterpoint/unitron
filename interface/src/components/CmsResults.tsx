type Props = {
  cms: string[]
}

export default function CmsResults({ cms }: Props) {
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
  return (
    <div className="bg-gray-50 p-4 rounded">
      <h3 className="font-medium mb-2">Content Management Systems</h3>
      {renderList(cms)}
    </div>
  )
}
