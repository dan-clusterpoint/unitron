export const COLOR_BLIND_PALETTE = {
  red: '#D55E00',
  amber: '#E69F00',
  green: '#009E73',
} as const

export type PaletteColor = keyof typeof COLOR_BLIND_PALETTE
