import CompanyProfileCard, { type CompanyProfileProps } from './CompanyProfileCard'
import DigitalScoreBar from './DigitalScoreBar'
import MiniRiskMatrix, { type RiskLevel } from './MiniRiskMatrix'
import StackDeltaRow, { type StackDeltaRowProps } from './StackDeltaRow'
import GrowthTriggersList, { type GrowthTriggersListProps } from './GrowthTriggersList'
import NextActionsChips, { type NextActionsChipsProps } from './NextActionsChips'

export interface ExecutiveSummaryCardProps {
  profile: CompanyProfileProps
  score: number
  risk?: { x: number; y: number; level: RiskLevel }
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
    <section aria-labelledby="exec-summary-heading">
      <h2 id="exec-summary-heading" className="sr-only">
        Executive Summary
      </h2>
      <article className="grid grid-cols-1 xs:grid-cols-2 gap-4 p-4 bg-white rounded shadow max-h-[320px] overflow-auto">
        <div className="xs:col-span-2">
          <CompanyProfileCard {...profile} />
        </div>
        <DigitalScoreBar score={score} />
        {risk && (
          <MiniRiskMatrix position={{ x: risk.x, y: risk.y }} level={risk.level} />
        )}
        {stack.length > 0 && (
          <div className="xs:col-span-2 space-y-1">
            {stack.map((s) => (
              <StackDeltaRow key={s.label} {...s} />
            ))}
          </div>
        )}
        {triggers.length > 0 && (
          <div className="xs:col-span-2">
            <GrowthTriggersList triggers={triggers} />
          </div>
        )}
        {actions.length > 0 && (
          <div className="xs:col-span-2">
            <NextActionsChips actions={actions} />
          </div>
        )}
      </article>
    </section>
  )
}
