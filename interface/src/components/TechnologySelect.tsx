import Autocomplete from '@mui/material/Autocomplete'
import TextField from '@mui/material/TextField'
import Chip from '@mui/material/Chip'
import { SUGGESTIONS, type StackItem } from '../utils/tech'

export type TechnologySelectProps = {
  value: StackItem[]
  onChange: (v: StackItem[]) => void
}

export default function TechnologySelect({ value, onChange }: TechnologySelectProps) {
  return (
    <div className="mt-4">
      <Autocomplete<StackItem, true, false, false>
        multiple
        options={SUGGESTIONS}
        groupBy={(option) => option.category}
        getOptionLabel={(option) => option.vendor}
        value={value}
        onChange={(_, newValue) => onChange(newValue)}
        isOptionEqualToValue={(option, val) => option.vendor === val.vendor}
        renderTags={(tagValue, getTagProps) =>
          tagValue.map((option, index) => (
            <Chip
              {...getTagProps({ index })}
              label={`${option.category} • ${option.vendor}`}
            />
          ))
        }
        renderInput={(params) => <TextField {...params} label="Technologies in use" />}
      />
    </div>
  )
}
