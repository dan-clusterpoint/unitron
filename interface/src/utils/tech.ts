export type StackItem = { category: string; vendor: string }

export const SUGGESTIONS: StackItem[] = [
  { category: 'Web Platform', vendor: 'Adobe Experience Manager' },
  { category: 'Web Platform', vendor: 'WordPress' },
  { category: 'Web Platform', vendor: 'Drupal' },
  { category: 'Web Platform', vendor: 'Shopify' },
  { category: 'Web Platform', vendor: 'Webflow' },

  { category: 'Tagging & Analytics', vendor: 'Google Analytics 4' },
  { category: 'Tagging & Analytics', vendor: 'Google Tag Manager' },
  { category: 'Tagging & Analytics', vendor: 'Adobe Analytics' },
  { category: 'Tagging & Analytics', vendor: 'Mixpanel' },
  { category: 'Tagging & Analytics', vendor: 'Amplitude' },

  { category: 'CDP & Event Streaming', vendor: 'Segment' },
  { category: 'CDP & Event Streaming', vendor: 'mParticle' },
  { category: 'CDP & Event Streaming', vendor: 'RudderStack' },
  { category: 'CDP & Event Streaming', vendor: 'Kafka' },
  { category: 'CDP & Event Streaming', vendor: 'Snowplow' },

  { category: 'Marketing Automation', vendor: 'HubSpot' },
  { category: 'Marketing Automation', vendor: 'Marketo' },
  { category: 'Marketing Automation', vendor: 'Braze' },
  { category: 'Marketing Automation', vendor: 'Iterable' },
  { category: 'Marketing Automation', vendor: 'Customer.io' },

  { category: 'CRM & RevOps', vendor: 'Salesforce' },
  { category: 'CRM & RevOps', vendor: 'HubSpot CRM' },
  { category: 'CRM & RevOps', vendor: 'Pipedrive' },
  { category: 'CRM & RevOps', vendor: 'Zoho CRM' },
  { category: 'CRM & RevOps', vendor: 'Close' },

  { category: 'Data Platform', vendor: 'Snowflake' },
  { category: 'Data Platform', vendor: 'Databricks' },
  { category: 'Data Platform', vendor: 'BigQuery' },
  { category: 'Data Platform', vendor: 'Redshift' },
  { category: 'Data Platform', vendor: 'PostgreSQL' },

  { category: 'BI & Activation', vendor: 'Looker' },
  { category: 'BI & Activation', vendor: 'Tableau' },
  { category: 'BI & Activation', vendor: 'Power BI' },
  { category: 'BI & Activation', vendor: 'Mode' },
  { category: 'BI & Activation', vendor: 'Hightouch' },
]

const ALIASES: Record<string, string> = {
  aem: 'Adobe Experience Manager',
  ga: 'Google Analytics 4',
  ga4: 'Google Analytics 4',
  'google analytics': 'Google Analytics 4',
  gtm: 'Google Tag Manager',
  'google tag manager': 'Google Tag Manager',
}

const VENDOR_CATEGORY = SUGGESTIONS.reduce<Record<string, string>>((acc, cur) => {
  acc[cur.vendor.toLowerCase()] = cur.category
  return acc
}, {})

export function normalizeStack(list: (string | null | undefined)[]): StackItem[] {
  const result: StackItem[] = []
  const seen = new Set<string>()
  for (const item of list) {
    if (!item) continue
    const trimmed = item.trim()
    if (!trimmed) continue
    const canonical = ALIASES[trimmed.toLowerCase()] ?? trimmed
    const key = canonical.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    const category = VENDOR_CATEGORY[key] || 'Other'
    result.push({ category, vendor: canonical })
  }
  return result
}

export function normalizeTechList(list: (string | null | undefined)[]): string[] {
  const result: string[] = []
  const seen = new Set<string>()
  for (const item of list) {
    if (!item) continue
    const trimmed = item.trim()
    if (!trimmed) continue
    const key = trimmed.toLowerCase()
    if (!seen.has(key)) {
      seen.add(key)
      result.push(trimmed)
    }
  }
  return result
}
