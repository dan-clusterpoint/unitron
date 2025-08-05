# API Notes

## POST /analyze

Returns the core analysis artifacts. The response now includes a
`snapshot` object that combines the profile, digital score, risk
assessment and suggested next actions.

### Snapshot schema

```json
{
  "profile": {},
  "digitalScore": {},
  "riskMatrix": {},
  "stackDelta": {},
  "growthTriggers": {},
  "nextActions": {}
}
```

## POST /generate

Optional field `martech_manual` (array of objects with `category` and `vendor`) allows overriding or supplementing detected vendors. A legacy array of strings is still accepted for backward compatibility. Manual items appear first and duplicate entries from detected list are removed.

### Example

```json
{
  "url": "https://example.com",
  "martech": { "core": ["Google Analytics"] },
  "martech_manual": [
    { "category": "analytics", "vendor": "Segment" }
  ],
  "cms": ["WordPress"]
}
```

## POST /snapshot

Assemble a final analysis snapshot from previously generated artifacts.

The request body matches the snapshot schema above and the endpoint responds
with the assembled object:

```json
{
  "snapshot": {
    "profile": {},
    "digitalScore": {},
    "riskMatrix": {},
    "stackDelta": {},
    "growthTriggers": [],
    "nextActions": {}
  }
}
```
