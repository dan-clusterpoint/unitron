#!/usr/bin/env bash
set -e

echo "=== HEALTH ==="
curl -sS https://$GATEWAY/health | jq .
curl -sS https://$MARTECH/health | jq .

echo "=== READY ==="
echo "=== ANALYZE adobe.com ==="
curl -sS -X POST https://$GATEWAY/analyze \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.adobe.com"}' | jq .

# end of file
