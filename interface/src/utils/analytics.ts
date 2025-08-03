export type AnalyticsEvent =
  | 'scope_open_popover'
  | 'scope_open_drawer'
  | 'domain_add'
  | 'domain_remove'
  | 'analysis_rerun'

export function track(event: AnalyticsEvent, payload?: Record<string, unknown>) {
  // In production this would send to analytics backend.
  // For now we log to console so tests can assert calls.
  console.log('track', event, payload)
}
