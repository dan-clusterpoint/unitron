type Props = {
  cms: string[]
  manualCms?: string
  setManualCms?: (v: string) => void
}

export default function CmsResults({ cms, manualCms, setManualCms }: Props) {
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
      {cms.length > 0 ? (
        renderList(cms)
      ) : (
        <div>
          {renderList(cms)}
          {setManualCms && (
            <div className="mt-2">
              <input
                aria-label="CMS"
                list="cms-list"
                value={manualCms}
                onChange={(e) => setManualCms(e.target.value)}
                placeholder="Enter CMS"
                className="border rounded p-2 w-full"
              />
              <datalist id="cms-list">
                <option value="WordPress" />
                <option value="Drupal" />
                <option value="Adobe Experience Manager" />
                <option value="Shopify" />
              </datalist>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
