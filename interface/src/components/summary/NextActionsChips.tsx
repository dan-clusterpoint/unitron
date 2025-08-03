import { useRef } from 'react'

export interface NextAction {
  label: string
  targetId: string
}

export interface NextActionsChipsProps {
  actions: NextAction[]
}

export default function NextActionsChips({ actions }: NextActionsChipsProps) {
  const btnRefs = useRef<Array<HTMLButtonElement | null>>([])

  function scroll(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  function handleKeyDown(
    e: React.KeyboardEvent<HTMLButtonElement>,
    idx: number,
  ) {
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      btnRefs.current[(idx + 1) % actions.length]?.focus()
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault()
      btnRefs.current[(idx - 1 + actions.length) % actions.length]?.focus()
    }
  }

  return (
    <ul className="flex flex-wrap gap-2" role="list">
      {actions.map((a, i) => (
        <li key={a.targetId}>
          <button
            ref={(el) => {
              btnRefs.current[i] = el
            }}
            onClick={() => scroll(a.targetId)}
            onKeyDown={(e) => handleKeyDown(e, i)}
            className="px-2 py-1 text-sm border rounded-full bg-gray-100"
          >
            {a.label}
          </button>
        </li>
      ))}
    </ul>
  )
}
