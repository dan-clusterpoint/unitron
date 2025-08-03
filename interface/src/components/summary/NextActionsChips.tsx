export interface NextAction {
  label: string
  targetId: string
}

export interface NextActionsChipsProps {
  actions: NextAction[]
}

export default function NextActionsChips({ actions }: NextActionsChipsProps) {
  function scroll(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }
  return (
    <div className="flex flex-wrap gap-2">
      {actions.map((a) => (
        <button
          key={a.targetId}
          onClick={() => scroll(a.targetId)}
          className="px-2 py-1 text-sm border rounded-full bg-gray-100"
        >
          {a.label}
        </button>
      ))}
    </div>
  )
}
