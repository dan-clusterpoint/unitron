import type { HTMLAttributes } from 'react'
import clsx from 'clsx'

export interface SheetProps extends HTMLAttributes<HTMLDivElement> {
  open: boolean
  onClose: () => void
}

export default function Sheet({ open, onClose, className, children }: SheetProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div
        className={clsx(
          'absolute right-0 top-0 h-full w-80 max-w-full bg-white shadow-lg p-4 overflow-auto',
          className,
        )}
      >
        <button
          aria-label="close"
          onClick={onClose}
          className="absolute top-2 right-2 text-xl"
        >
          ×
        </button>
        {children}
      </div>
    </div>
  )
}
