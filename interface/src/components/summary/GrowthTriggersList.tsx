import { useRef, useState } from 'react'
import Sheet from '../ui/sheet'

export interface GrowthTriggersListProps {
  triggers: string[]
}

export default function GrowthTriggersList({ triggers }: GrowthTriggersListProps) {
  const [open, setOpen] = useState(false)
  const visible = triggers.slice(0, 3)
  const hidden = triggers.slice(3)
  const itemRefs = useRef<Array<HTMLLIElement | null>>([])

  function handleKeyDown(
    e: React.KeyboardEvent<HTMLLIElement>,
    idx: number,
  ) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      itemRefs.current[(idx + 1) % visible.length]?.focus()
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      itemRefs.current[(idx - 1 + visible.length) % visible.length]?.focus()
    }
  }
  return (
    <div className="text-sm">
      <ul className="list-disc ml-4 space-y-1" role="list">
        {visible.map((t, i) => (
          <li
            key={i}
            ref={(el) => {
              itemRefs.current[i] = el
            }}
            tabIndex={0}
            onKeyDown={(e) => handleKeyDown(e, i)}
          >
            {t}
          </li>
        ))}
      </ul>
      {hidden.length > 0 && (
        <>
          <button
            onClick={() => setOpen(true)}
            className="text-blue-600 text-sm mt-1"
          >
            +{hidden.length}
          </button>
          <Sheet open={open} onClose={() => setOpen(false)}>
            <h2 className="font-medium mb-2">Growth Triggers</h2>
            <ul className="list-disc ml-4 space-y-1">
              {triggers.map((t, i) => (
                <li key={i}>{t}</li>
              ))}
            </ul>
          </Sheet>
        </>
      )}
    </div>
  )
}
