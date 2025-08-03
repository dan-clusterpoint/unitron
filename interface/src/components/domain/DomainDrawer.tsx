import { useState } from 'react'
import { createPortal } from 'react-dom'
import { useDomains } from '../../contexts/DomainContext'
import { track } from '../../utils/analytics'

export default function DomainDrawer({
  onClose,
  onRerun,
}: {
  onClose: () => void
  onRerun: () => void
}) {
  const { domains, setDomains } = useDomains()
  const [text, setText] = useState(domains.join('\n'))

  function save() {
    const list = text
      .split(/\n+/)
      .map((d) => d.trim())
      .filter(Boolean)
    setDomains(list)
    track('analysis_rerun')
    onRerun()
    onClose()
  }

  return createPortal(
    <div className="fixed inset-0 bg-black/50 flex justify-end" role="dialog">
      <div className="bg-white w-[400px] p-4 h-full overflow-y-auto">
        <h2 className="font-medium mb-2">Domain Scope</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="border w-full h-64 mb-2"
        />
        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="px-3 py-1 border rounded">
            Cancel
          </button>
          <button onClick={save} className="px-3 py-1 border rounded bg-blue-600 text-white">
            Save & Rerun
          </button>
        </div>
      </div>
    </div>,
    document.body,
  )
}