import { HTMLAttributes } from 'react'
import clsx from 'clsx'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'secondary' | 'outline'
}

export function Badge({ className, variant = 'default', ...props }: BadgeProps) {
  const base = 'inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-semibold'
  const variants: Record<string, string> = {
    default: 'bg-primary text-white border-transparent',
    secondary: 'bg-secondary text-white border-transparent',
    outline: 'border current text-current',
  }
  return <span className={clsx(base, variants[variant], className)} {...props} />
}
