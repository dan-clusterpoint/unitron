#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

usage() { echo "Usage: $0 gateway|martech|property|all" >&2; exit 1; }
svc=${1:-}; [ -z "$svc" ] && usage

run_one() {
  local s="$1"
  local dir="services/$s"
  local port
  port=$(shuf -i 5000-5999 -n 1)
  echo "-- Building $s"
  docker build -t "unitron_$s:test" "$dir" >/dev/null
  cid=$(docker run -d -p "$port:8000" -e PORT=8000 "unitron_$s:test")
  trap "docker rm -f $cid >/dev/null" RETURN
  sleep 2
  curl -fs "http://localhost:$port/health" >/dev/null
  curl -I "http://localhost:$port/docs" >/dev/null
  case $s in
    gateway)
      curl -fs -X POST "http://localhost:$port/analyze" \
        -H 'Content-Type: application/json' \
        -d '{"property":{"domain":"example.com"},"martech":{"url":"https://example.com"}}' >/dev/null
      ;;
    martech)
      curl -fs -X POST "http://localhost:$port/analyze" \
        -H 'Content-Type: application/json' \
        -d '{"url":"https://example.com"}' >/dev/null
      ;;
    property)
      curl -fs -X POST "http://localhost:$port/analyze" \
        -H 'Content-Type: application/json' \
        -d '{"domain":"example.com"}' >/dev/null
      ;;
  esac
  docker rm -f "$cid" >/dev/null
  echo "$s ok"
}

if [ "$svc" = "all" ]; then
  for s in gateway martech property; do
    run_one "$s"
  done
else
  run_one "$svc"
fi
