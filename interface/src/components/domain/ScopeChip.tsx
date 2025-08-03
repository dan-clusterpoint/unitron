import { useState, useEffect, lazy, Suspense } from 'react'
import { useDomains } from '../../contexts/DomainContext'
import { track } from '../../utils/analytics'

const DomainPopover = lazy(() => import('./DomainPopover'))

export default function ScopeChip({ onRerun }: { onRerun: () => void }) {
  const { domains } = useDomains()
  const [open, setOpen] = useState(false)

  function toggle() {
    setOpen((o) => !o)
    if (!open) track('scope_open_popover')
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.metaKey && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        toggle()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  })

  return (
    <>
      <button
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={toggle}
        className="px-2 py-1 border rounded mx-3"
      >
        {domains.length} Domains ▾
      </button>
      {open && (
        <Suspense fallback={null}>
          <DomainPopover onClose={() => setOpen(false)} onRerun={onRerun} />
        </Suspense>
      )}
    </>
  )
}