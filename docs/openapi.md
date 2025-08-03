# Gateway API Notes

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
