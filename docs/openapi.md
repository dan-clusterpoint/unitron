# Gateway API Notes

## POST /generate

Optional field `martech_manual` (array of strings) allows overriding or supplementing detected vendors. Manual items appear first and duplicate entries from detected list are removed.

### Example

```json
{
  "url": "https://example.com",
  "martech": { "core": ["Google Analytics"] },
  "martech_manual": ["Segment"],
  "cms": ["WordPress"]
}
```
