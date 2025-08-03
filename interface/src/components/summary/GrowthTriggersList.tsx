import { useState } from 'react'
import Sheet from '../ui/sheet'

export interface GrowthTriggersListProps {
  triggers: string[]
}

export default function GrowthTriggersList({ triggers }: GrowthTriggersListProps) {
  const [open, setOpen] = useState(false)
  const visible = triggers.slice(0, 3)
  const hidden = triggers.slice(3)
  return (
    <div className="text-sm">
      <ul className="list-disc ml-4 space-y-1">
        {visible.map((t, i) => (
          <li key={i}>{t}</li>
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
