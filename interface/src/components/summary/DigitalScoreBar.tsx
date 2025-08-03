import clsx from 'clsx'

export interface DigitalScoreBarProps {
  score: number
}

export default function DigitalScoreBar({ score }: DigitalScoreBarProps) {
  const bounded = Math.max(0, Math.min(100, score))
  const color =
    bounded >= 80 ? 'bg-green-500' : bounded >= 50 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div>
      <div className="text-sm mb-1">Digital Score: {bounded}</div>
      <div className="h-2 bg-gray-200 rounded">
        <div
          className={clsx('h-full rounded', color)}
          style={{ width: `${bounded}%` }}
        />
      </div>
    </div>
  )
}
