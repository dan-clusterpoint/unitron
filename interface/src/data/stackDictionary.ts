export type StackCategory =
  | 'Web Platform'
  | 'Tagging & Analytics'
  | 'A/B & Personalization'
  | 'CDP & Event Streaming'
  | 'Marketing Automation'
  | 'CRM & RevOps'
  | 'Data Platform'
  | 'BI & Activation'
  | 'Observability & Performance'
  | 'Cloud & Edge'
  | 'Ads & Attribution'
  | 'Security & Consent'

export interface StackVendor {
  vendor: string
  category: StackCategory
  synonyms?: string[]
}

export const STACK_VENDORS: StackVendor[] = [
  {
    vendor: 'Adobe Experience Manager',
    category: 'Web Platform',
    synonyms: ['AEM', 'Adobe CQ'],
  },
  {
    vendor: 'Google Analytics 4',
    category: 'Tagging & Analytics',
    synonyms: ['GA4', 'Google Analytics', 'GA'],
  },
  { vendor: 'Segment', category: 'CDP & Event Streaming' },
  { vendor: 'Snowflake', category: 'Data Platform' },
]
