import { STACK_VENDORS, StackVendor } from '../data/stackDictionary'

export function normalizeStackInput(
  input: string
): StackVendor | { vendor: string; category: 'Uncategorized' } {
  const trimmed = input.trim()
  const lower = trimmed.toLowerCase()
  for (const item of STACK_VENDORS) {
    if (item.vendor.toLowerCase() === lower) {
      return { vendor: item.vendor, category: item.category }
    }
    if (item.synonyms?.some((s) => s.toLowerCase() === lower)) {
      return { vendor: item.vendor, category: item.category }
    }
  }
  return { vendor: trimmed, category: 'Uncategorized' }
}
