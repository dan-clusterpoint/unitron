import type { CompanyProfileProps } from '../components/summary'

export interface Snapshot {
  profile: CompanyProfileProps
  digitalScore: number
  vendors: string[]
  growthTriggers: string[]
  seo?: {
    robotsTxt?: boolean
    sitemapXml?: boolean
  }
}
