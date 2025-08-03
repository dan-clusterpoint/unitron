import { useState, useRef, useEffect, lazy, Suspense } from 'react'
import { createPortal } from 'react-dom'
import { useDomains } from '../../contexts/DomainContext'
import { track } from '../../utils/analytics'

const DomainDrawer = lazy(() => import('./DomainDrawer'))

export default function DomainPopover({
  onClose,
  onRerun = () => {},
}: {
  onClose: () => void
  onRerun?: () => void
}) {
  const { domains, addDomain, removeDomain } = useDomains()
  const [input, setInput] = useState('')
  const [drawer, setDrawer] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
      if (e.key.toLowerCase() === 'd') {
        e.preventDefault()
        setDrawer(true)
        track('scope_open_drawer')
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  useEffect(() => {
    function handle(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose()
      }
    }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [onClose])

  function handleAdd() {
    if (input.trim()) {
      addDomain(input.trim())
      track('domain_add')
      setInput('')
    }
  }

  return (
    <>
      {createPortal(
        <div
          ref={ref}
          className="absolute top-12 right-4 w-[280px] bg-white border p-4 rounded shadow"
          role="dialog"
        >
          <ul className="mb-2">
            {domains.slice(0, 5).map((d) => (
              <li key={d} className="flex justify-between items-center">
                <span>{d}</span>
                <button
                  aria-label="Remove"
                  onClick={() => {
                    removeDomain(d)
                    track('domain_remove')
                  }}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
          <div className="flex gap-2 mb-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="border flex-1 px-1"
              placeholder="Add domain"
            />
            <button onClick={handleAdd} className="px-2 border rounded">
              Add
            </button>
          </div>
          <button
            className="underline text-sm"
            onClick={() => {
              setDrawer(true)
              track('scope_open_drawer')
            }}
          >
            Open Drawer
          </button>
        </div>,
        document.body,
      )}
      {drawer && (
        <Suspense fallback={null}>
          <DomainDrawer onClose={() => setDrawer(false)} onRerun={onRerun} />
        </Suspense>
      )}
    </>
  )
}
