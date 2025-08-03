import { COLOR_BLIND_PALETTE } from './palette'

export interface DigitalScoreBarProps {
  score: number
}

export default function DigitalScoreBar({ score }: DigitalScoreBarProps) {
  const bounded = Math.max(0, Math.min(100, score))
  const color =
    bounded >= 80
      ? COLOR_BLIND_PALETTE.green
      : bounded >= 50
        ? COLOR_BLIND_PALETTE.amber
        : COLOR_BLIND_PALETTE.red
  return (
    <div>
      <div className="text-sm mb-1">Digital Score: {bounded}</div>
      <div className="h-2 bg-gray-200 rounded">
        <div
          className="h-full rounded"
          style={{ width: `${bounded}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
