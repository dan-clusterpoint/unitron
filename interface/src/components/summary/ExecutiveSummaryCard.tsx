import CompanyProfileCard, { type CompanyProfileProps } from './CompanyProfileCard'
import DigitalScoreBar from './DigitalScoreBar'
import GrowthTriggersList, { type GrowthTriggersListProps } from './GrowthTriggersList'

export interface ExecutiveSummaryCardProps {
  profile: CompanyProfileProps
  score: number
  vendors: string[]
  triggers?: GrowthTriggersListProps['triggers']
}

export default function ExecutiveSummaryCard({
  profile,
  score,
  vendors,
  triggers = [],
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
        {vendors.length > 0 && (
          <div className="xs:col-span-2 space-y-1 text-sm">
            {vendors.map((v) => (
              <div key={v}>{v}</div>
            ))}
          </div>
        )}
        {triggers.length > 0 && (
          <div className="xs:col-span-2">
            <GrowthTriggersList triggers={triggers} />
          </div>
        )}
      </article>
    </section>
  )
}
