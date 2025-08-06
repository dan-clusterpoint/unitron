import { useState } from 'react'
import { Badge } from '../ui/badge'

export interface EditableMartechListProps {
  value: string[]
  onChange: (v: string[]) => void
}

export default function EditableMartechList({ value, onChange }: EditableMartechListProps) {
  const [input, setInput] = useState('')

  function addVendor() {
    const v = input.trim()
    if (!v || value.includes(v)) {
      setInput('')
      return
    }
    onChange([...value, v])
    setInput('')
  }

  function removeVendor(v: string) {
    onChange(value.filter((i) => i !== v))
  }

  function updateVendor(idx: number, v: string) {
    const copy = [...value]
    copy[idx] = v
    onChange(copy)
  }

  return (
    <div className="bg-gray-50 p-4 rounded">
      <h3 className="font-medium mb-2">Martech Vendors</h3>
      <div className="flex flex-wrap gap-2 mb-2">
        {value.map((vendor, idx) => (
          <Badge key={vendor} className="gap-1">
            <input
              aria-label={`vendor-${idx}`}
              value={vendor}
              onChange={(e) => updateVendor(idx, e.target.value)}
              className="bg-transparent focus:outline-none"
            />
            <button
              type="button"
              aria-label={`remove ${vendor}`}
              className="ml-1"
              onClick={() => removeVendor(vendor)}
            >
              ×
            </button>
          </Badge>
        ))}
      </div>
      <input
        aria-label="add vendor"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            addVendor()
          }
        }}
        className="border rounded p-1 text-sm"
        placeholder="Add vendor"
      />
    </div>
  )
}
