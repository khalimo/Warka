#!/usr/bin/env bash
set -u

FRONTEND_URL="${FRONTEND_URL:-https://www.warkasta.com}"
API_BASE_URL="${API_BASE_URL:-https://api.warkasta.com}"

failures=0

check_url() {
  local label="$1"
  local url="$2"
  local expected_prefix="$3"
  local status
  local error_file

  error_file="$(mktemp)"
  status="$(curl -L -sS -o /tmp/warka-smoke-response.txt -w "%{http_code}" --max-time 25 "$url" 2>"$error_file" || true)"

  if [[ "$status" == "$expected_prefix"* ]]; then
    printf "OK   %s -> %s\n" "$label" "$status"
  else
    printf "FAIL %s -> %s (%s)\n" "$label" "${status:-curl failed}" "$url"
    if [[ -s "$error_file" ]]; then
      sed 's/^/     /' "$error_file"
    fi
    failures=$((failures + 1))
  fi

  rm -f "$error_file"
}

printf "Warka production smoke check\n"
printf "Frontend: %s\n" "$FRONTEND_URL"
printf "API:      %s\n\n" "$API_BASE_URL"

check_url "frontend" "$FRONTEND_URL" "2"
check_url "backend health" "$API_BASE_URL/api/health" "2"
check_url "latest stories" "$API_BASE_URL/api/stories/latest?limit=1&offset=0" "2"
check_url "clusters" "$API_BASE_URL/api/clusters?limit=1&offset=0" "2"
check_url "homepage data" "$API_BASE_URL/api/home" "2"

if [[ "$failures" -gt 0 ]]; then
  printf "\n%d check(s) failed.\n" "$failures"
  printf "If only homepage data fails, run: curl -X POST %s/api/ingest\n" "$API_BASE_URL"
  exit 1
fi

printf "\nAll production checks passed.\n"
