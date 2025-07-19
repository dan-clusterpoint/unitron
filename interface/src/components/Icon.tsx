import { ComponentType } from 'react'

export type IconProps = {
  icon: ComponentType<React.SVGProps<SVGSVGElement>>
  className?: string
}

export default function Icon({ icon: IconComponent, className = '' }: IconProps) {
  const base = 'w-8 h-8 md:w-6 md:h-6'
  return <IconComponent className={`${base} ${className}`} />
}
