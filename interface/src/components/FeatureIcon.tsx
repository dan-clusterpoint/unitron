import type { ComponentType } from 'react'

export interface FeatureIconProps {
  Icon: ComponentType<React.SVGProps<SVGSVGElement>>
}

export default function FeatureIcon({ Icon }: FeatureIconProps) {
  return (
    <Icon className="w-8 h-8 md:w-6 md:h-6 lg:w-5 lg:h-5 text-primary transform transition-transform lg:scale-90" />
  )
}
