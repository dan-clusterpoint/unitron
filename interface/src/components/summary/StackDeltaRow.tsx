import { PlusCircleIcon, MinusCircleIcon, ArrowPathIcon } from '@heroicons/react/24/solid'

export interface StackDeltaRowProps {
  label: string
  status: 'added' | 'removed' | 'changed'
}

export default function StackDeltaRow({ label, status }: StackDeltaRowProps) {
  const icon =
    status === 'added' ? (
      <PlusCircleIcon className="w-5 h-5 text-green-600" />
    ) : status === 'removed' ? (
      <MinusCircleIcon className="w-5 h-5 text-red-600" />
    ) : (
      <ArrowPathIcon className="w-5 h-5 text-yellow-600" />
    )
  return (
    <div className="flex items-center gap-2 text-sm">
      {icon}
      <span>{label}</span>
    </div>
  )
}
