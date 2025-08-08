import type { HTMLAttributes } from 'react'
import clsx from 'clsx'

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value?: number
  max?: number
}

export function Progress({ className, value = 0, max = 100, ...props }: ProgressProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className={clsx('w-full bg-gray-200 rounded', className)} {...props}>
      <div className="h-2 bg-primary rounded" style={{ width: `${pct}%` }} />
    </div>
  )
}
