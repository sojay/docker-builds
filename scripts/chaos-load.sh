#!/usr/bin/env bash
# Sustained load driver for the Sentry alert exercises in
# docs/sentry-alert-exercises.md
#
#   scripts/chaos-load.sh check                 # one hit per route, assert codes
#   scripts/chaos-load.sh errors                # default 300s @ 2 rps
#   DURATION=1800 RPS=5 scripts/chaos-load.sh mixed
#
# Alert thresholds are per-minute or per-hour, so a one-shot curl will never
# fire them. That is what this script is for: it keeps the signal going long
# enough for a rule to evaluate.
set -uo pipefail

API=${API:-http://localhost:5000}
DURATION=${DURATION:-300}   # seconds
RPS=${RPS:-2}               # requests per second (approximate)
SCENARIO=${1:-help}

hit() { curl -s -m 90 -o /dev/null -w '%{http_code}' "$API$1"; }

usage() {
    cat <<'USAGE'
scenarios:
  check      one request per route, assert expected status codes, exit non-zero on mismatch
  errors     /api/chaos/recursion            -> 500s, one high-volume issue
  slow       /api/chaos/slow?seconds=3       -> p95 transaction duration
  nplusone   /api/chaos/nplusone?rows=25     -> N+1 performance issue
  mixed      ~20% 500s, 80% 200s             -> failure_rate() metric alert
  leak       /api/chaos/memory?mb=50         -> OOM the api container (uptime/downtime)
  burst      errors as fast as possible      -> rate limiting / spike protection

env: API (default http://localhost:5000)  DURATION (300)  RPS (2)
USAGE
}

# Runnable check: fails loudly if a route or the stack is broken, so a silent
# "no events in Sentry" is never blamed on the exercise doc.
run_check() {
    local fail=0 code
    while read -r path want; do
        code=$(hit "$path")
        if [ "$code" = "$want" ]; then
            printf 'ok    %-34s %s\n' "$path" "$code"
        else
            printf 'FAIL  %-34s got %s want %s\n' "$path" "$code" "$want"
            fail=1
        fi
    done <<'ROUTES'
/api/categories 200
/api/debug-sentry 500
/api/chaos/slow?seconds=1 200
/api/chaos/postgres 200
/api/chaos/nplusone?rows=5 200
/api/chaos/thread 200
/api/chaos/unhandled-async 200
/api/chaos/memory?mb=1 200
/api/chaos/recursion 500
ROUTES
    [ "$fail" -eq 0 ] || { echo "check FAILED - is the stack up? (docker compose ps)"; return 1; }
    echo "check passed"
}

run_loop() {
    local path=$1 deadline=$(( $(date +%s) + DURATION )) n=0
    echo "-> $path  for ${DURATION}s at ~${RPS}/s  (ctrl-c to stop)"
    while [ "$(date +%s)" -lt "$deadline" ]; do
        for _ in $(seq "$RPS"); do hit "$path" >/dev/null & done
        wait
        n=$(( n + RPS ))
        printf '\r   %d requests' "$n"
        sleep 1
    done
    printf '\n   done: %d requests\n' "$n"
}

case "$SCENARIO" in
    check)    run_check ;;
    errors)   run_loop '/api/chaos/recursion' ;;
    slow)     run_loop '/api/chaos/slow?seconds=3' ;;
    nplusone) run_loop '/api/chaos/nplusone?rows=25' ;;
    leak)     RPS=1 run_loop '/api/chaos/memory?mb=50' ;;
    burst)    DURATION=${DURATION} RPS=50 run_loop '/api/chaos/recursion' ;;
    mixed)
        deadline=$(( $(date +%s) + DURATION ))
        echo "-> mixed 20% errors for ${DURATION}s at ~${RPS}/s"
        while [ "$(date +%s)" -lt "$deadline" ]; do
            for i in $(seq "$RPS"); do
                if [ $(( RANDOM % 5 )) -eq 0 ]; then hit '/api/chaos/recursion' >/dev/null &
                else hit '/api/categories' >/dev/null & fi
            done
            wait; sleep 1
        done
        echo "   done"
        ;;
    *) usage; [ "$SCENARIO" = help ] && exit 0 || exit 2 ;;
esac
