import { useState } from 'react'
import catalogData from '../data/martech_catalog.json'

export interface MartechItem {
  category: string
  vendor: string
}

interface Props {
  value: MartechItem[]
  onChange: (v: MartechItem[]) => void
}

const CATEGORIES = Object.entries(catalogData).filter(([key]) => key !== '_comment') as [string, { label: string; vendors: string[] }][]

export default function MartechCategorySelector({ value, onChange }: Props) {
  const [inputs, setInputs] = useState<Record<string, string>>({})

  function isSelected(category: string, vendor: string) {
    return value.some((v) => v.category === category && v.vendor === vendor)
  }

  function toggle(category: string, vendor: string, checked: boolean) {
    const exists = isSelected(category, vendor)
    if (checked && !exists) {
      onChange([...value, { category, vendor }])
    } else if (!checked && exists) {
      onChange(value.filter((v) => !(v.category === category && v.vendor === vendor)))
    }
  }

  function addOther(category: string) {
    const v = (inputs[category] || '').trim()
    if (!v) return
    const current = CATEGORIES.find(([key]) => key === category)
    if (current && !current[1].vendors.includes(v)) {
      current[1].vendors.push(v)
    }
    setInputs((i) => ({ ...i, [category]: '' }))
    toggle(category, v, true)
  }

  const [active, setActive] = useState(CATEGORIES[0][0])

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-2" role="tablist">
        {CATEGORIES.map(([key, info]) => (
          <button
            key={key}
            role="tab"
            className={`px-2 py-1 rounded border ${active === key ? 'bg-gray-200' : ''}`}
            onClick={() => setActive(key)}
            aria-selected={active === key}
          >
            {info.label}
          </button>
        ))}
      </div>
      {CATEGORIES.map(([key, info]) => (
        <div key={key} role="tabpanel" hidden={active !== key} className="mb-4">
          <div className="flex flex-wrap gap-2">
            {info.vendors.map((v) => (
              <label key={v} className="border rounded px-2 py-1 text-sm flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={isSelected(key, v)}
                  onChange={(e) => toggle(key, v, e.target.checked)}
                />
                {v}
              </label>
            ))}
            <div className="flex items-center gap-1">
              <input
                aria-label={`${key}-other`}
                value={inputs[key] || ''}
                onChange={(e) => setInputs((i) => ({ ...i, [key]: e.target.value }))}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addOther(key)
                  }
                }}
                className="border rounded px-1 py-0.5 text-sm"
                placeholder="Other..."
              />
              <button
                type="button"
                className="border rounded px-1 text-sm"
                onClick={() => addOther(key)}
              >
                Add
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
