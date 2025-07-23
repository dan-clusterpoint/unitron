#!/bin/bash
# Simple gateway smoke test script.

set -o pipefail

if [ -z "$GATEWAY_URL" ]; then
  echo "GATEWAY_URL environment variable not set" >&2
  exit 1
fi

curl -i "$GATEWAY_URL/health"
if [ $? -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi

curl -i "$GATEWAY_URL/ready"
if [ $? -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi

curl -X POST "$GATEWAY_URL/analyze" -d '{"domain":"example.com"}' -H 'Content-Type: application/json'
if [ $? -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi

curl -X POST "$GATEWAY_URL/analyze" -d '{"domain":"not_a_domain"}' -H 'Content-Type: application/json'
if [ $? -eq 0 ]; then
  echo "PASS"
else
  echo "FAIL"
fi
