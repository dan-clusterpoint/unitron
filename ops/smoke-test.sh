#!/usr/bin/env bash
set -e

echo "=== HEALTH ==="
curl -sS https://$GATEWAY/health | jq .
curl -sS https://$MARTECH/health | jq .
curl -sS https://$PROPERTY/health | jq .

echo "=== READY ==="
curl -sS https://$GATEWAY/ready | jq .

echo "=== ANALYZE adobe.com ==="
curl -sS -X POST https://$GATEWAY/analyze \
  -H "Content-Type: application/json" \
  -d '{"property":{"domain":"adobe.com"}, "martech":{"url":"https://www.adobe.com"}}' | jq .

# end of file
