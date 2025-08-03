import type { JSX } from 'react'
import { COLOR_BLIND_PALETTE } from './palette'

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
          className="w-3 h-3 border"
          style={{
            backgroundColor: active
              ? COLOR_BLIND_PALETTE.red
              : '#f3f4f6',
          }}
        />
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
