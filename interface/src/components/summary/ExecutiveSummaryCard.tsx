import CompanyProfileCard, { type CompanyProfileProps } from './CompanyProfileCard'
import DigitalScoreBar from './DigitalScoreBar'
import MiniRiskMatrix, { type MiniRiskMatrixProps } from './MiniRiskMatrix'
import StackDeltaRow, { type StackDeltaRowProps } from './StackDeltaRow'
import GrowthTriggersList, { type GrowthTriggersListProps } from './GrowthTriggersList'
import NextActionsChips, { type NextActionsChipsProps } from './NextActionsChips'

export interface ExecutiveSummaryCardProps {
  profile: CompanyProfileProps
  score: number
  risk?: MiniRiskMatrixProps['position']
  stack: StackDeltaRowProps[]
  triggers: GrowthTriggersListProps['triggers']
  actions: NextActionsChipsProps['actions']
}

export default function ExecutiveSummaryCard({
  profile,
  score,
  risk,
  stack,
  triggers,
  actions,
}: ExecutiveSummaryCardProps) {
  return (
    <article className="grid grid-cols-2 gap-4 p-4 bg-white rounded shadow max-h-[320px] overflow-auto">
      <div className="col-span-2">
        <CompanyProfileCard {...profile} />
      </div>
      <DigitalScoreBar score={score} />
      <MiniRiskMatrix position={risk} />
      <div className="col-span-2 space-y-1">
        {stack.map((s) => (
          <StackDeltaRow key={s.label} {...s} />
        ))}
      </div>
      <div className="col-span-2">
        <GrowthTriggersList triggers={triggers} />
      </div>
      <div className="col-span-2">
        <NextActionsChips actions={actions} />
      </div>
    </article>
  )
}
