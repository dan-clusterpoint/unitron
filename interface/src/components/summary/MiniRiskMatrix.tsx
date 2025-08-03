import clsx from 'clsx'

export interface MiniRiskMatrixProps {
  position?: { x: number; y: number }
  onClick?: () => void
}

export default function MiniRiskMatrix({ position, onClick }: MiniRiskMatrixProps) {
  function handleClick() {
    if (onClick) onClick()
    else document.getElementById('healthchecks')?.scrollIntoView({ behavior: 'smooth' })
  }
  const cells: JSX.Element[] = []
  for (let y = 0; y < 3; y++) {
    for (let x = 0; x < 3; x++) {
      const active = position && position.x === x && position.y === y
      cells.push(
        <div
          key={`${x}-${y}`}
          className={clsx(
            'w-3 h-3 border',
            active ? 'bg-red-500' : 'bg-gray-100',
          )}
        />,
      )
    }
  }
  return (
    <button
      aria-label="healthchecks"
      onClick={handleClick}
      className="grid grid-cols-3 grid-rows-3 gap-0.5"
    >
      {cells}
    </button>
  )
}
