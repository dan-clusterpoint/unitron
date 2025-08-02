import { useState } from 'react'
import Autocomplete from '@mui/material/Autocomplete'
import TextField from '@mui/material/TextField'
import Chip from '@mui/material/Chip'
import { normalizeTechList } from '../utils/tech'

const SUGGESTIONS = [
  { group: 'Core analytics/marketing', label: 'Google Analytics' },
  { group: 'Core analytics/marketing', label: 'Adobe Analytics' },
  { group: 'Core analytics/marketing', label: 'Segment' },
  { group: 'Core analytics/marketing', label: 'Mixpanel' },
  { group: 'Core analytics/marketing', label: 'Amplitude' },
  { group: 'Core analytics/marketing', label: 'HubSpot' },
  { group: 'Core analytics/marketing', label: 'Marketo' },
  { group: 'Core analytics/marketing', label: 'Salesforce' },
  { group: 'Core analytics/marketing', label: 'AEM' },
  { group: 'Core analytics/marketing', label: 'GA4' },
  { group: 'Core analytics/marketing', label: 'GTM' },
  { group: 'Core analytics/marketing', label: 'Looker' },
  { group: 'Core analytics/marketing', label: 'Tableau' },
  { group: 'Core analytics/marketing', label: 'Snowflake' },
  { group: 'Core analytics/marketing', label: 'Databricks' },
  { group: 'Core analytics/marketing', label: 'Shopify' },
  { group: 'Core analytics/marketing', label: 'BigQuery' },
  { group: 'Core analytics/marketing', label: 'Redshift' },
  { group: 'Core analytics/marketing', label: 'Braze' },
  { group: 'Core analytics/marketing', label: 'Iterable' },
]

type TechnologySelectProps = {
  value: string[]
  onChange: (v: string[]) => void
}

export default function TechnologySelect({ value, onChange }: TechnologySelectProps) {
  const [showEmptyNote, setShowEmptyNote] = useState(false)

  function handleChange(_: unknown, newValue: (string | { label: string })[]) {
    const mapped = newValue.map((v) => (typeof v === 'string' ? v : v.label))
    const normalized = normalizeTechList(mapped)
    setShowEmptyNote(mapped.some((v) => !v || !v.trim()))
    onChange(normalized)
  }

  return (
    <div className="mt-4">
      <Autocomplete
        multiple
        freeSolo
        options={SUGGESTIONS}
        groupBy={(option) => (option as any).group}
        getOptionLabel={(option) => (typeof option === 'string' ? option : option.label)}
        value={value}
        onChange={handleChange as any}
        renderTags={(tagValue, getTagProps) =>
          tagValue.map((option, index) => (
            <Chip {...getTagProps({ index })} label={option} />
          ))
        }
        renderInput={(params) => <TextField {...params} label="Technologies in use" />}
      />
      {showEmptyNote && (
        <div className="text-sm text-red-600 mt-1">Empty value ignored</div>
      )}
    </div>
  )
}
