import { PlusCircleIcon, MinusCircleIcon, ArrowPathIcon } from '@heroicons/react/24/solid'
import { COLOR_BLIND_PALETTE } from './palette'

export interface StackDeltaRowProps {
  label: string
  status: 'added' | 'removed' | 'changed'
}

export default function StackDeltaRow({ label, status }: StackDeltaRowProps) {
  const icon =
    status === 'added' ? (
      <PlusCircleIcon
        className="w-5 h-5"
        style={{ color: COLOR_BLIND_PALETTE.green }}
      />
    ) : status === 'removed' ? (
      <MinusCircleIcon
        className="w-5 h-5"
        style={{ color: COLOR_BLIND_PALETTE.red }}
      />
    ) : (
      <ArrowPathIcon
        className="w-5 h-5"
        style={{ color: COLOR_BLIND_PALETTE.amber }}
      />
    )
  return (
    <div className="flex items-center gap-2 text-sm">
      {icon}
      <span>{label}</span>
    </div>
  )
}
