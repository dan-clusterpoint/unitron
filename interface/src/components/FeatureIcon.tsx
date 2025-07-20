import type { ComponentType } from 'react'
import clsx from 'clsx'

export interface FeatureIconProps {
  Icon: ComponentType<React.SVGProps<SVGSVGElement>>
  className?: string
}

export default function FeatureIcon({ Icon, className = '' }: FeatureIconProps) {
  return (
    <Icon
      className={clsx(
        'feature-icon text-inherit transform transition-transform lg:scale-90',
        className
      )}
    />
  )
}
