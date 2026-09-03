# Sentry Alert Exercises

Hands-on exercises for triggering, receiving, and debugging Sentry alerts using
this bookstore stack. Each exercise names the alert rule to create, the command
that generates the signal, and what you should see. Do them in order — later
exercises assume the rules from earlier ones exist.

Why a load script: almost every alert condition evaluates over a time window
(events per minute, p95 over 5 minutes). A single curl never fires anything.
`scripts/chaos-load.sh` keeps the signal going long enough for rules to evaluate.

## Prerequisites

```bash
docker compose --env-file ui/.env.local up --build -d
scripts/chaos-load.sh check        # all routes must pass before you start
```

- Two Sentry projects: one Python (the api DSN in `api/.env`), one
  React/JavaScript (the DSN in `ui/.env.local`).
- An alert notification channel you can actually watch: email is fine; Slack
  integration is better practice since that is what customers use.
- Chaos routes are enabled by the compose file (`ENABLE_CHAOS_ROUTES=true`).

Script usage:

```bash
scripts/chaos-load.sh <scenario>            # 300s at 2 rps by default
DURATION=1800 RPS=5 scripts/chaos-load.sh <scenario>
```

---

## Exercise 1 — Issue alert: a new issue is created

**Rule** (Python project → Alerts → Create Alert → Issues):
- When: *A new issue is created*
- Then: notify you

**Trigger:**

```bash
curl http://localhost:5000/api/debug-sentry
```

**Expect:** one alert within ~a minute. Trigger it again — no second alert,
because the issue is no longer *new*. That distinction (issue-level vs
event-level) is behind a large share of "Sentry stopped alerting me" tickets.

**Follow-up:** delete the issue in Sentry, trigger again, watch the alert fire
again. Deleting resets "new"; resolving does not (that is Exercise 3).

## Exercise 2 — Issue alert: event frequency threshold

**Rule:**
- When: *The issue is seen more than 100 times in one hour*
- Then: notify you

**Trigger:**

```bash
DURATION=120 RPS=2 scripts/chaos-load.sh errors     # ~240 events
```

**Expect:** one alert once the count crosses 100. Note the alert contains the
issue link, not 100 separate notifications — look at the rule's *action
interval* (default: at most once per 30 minutes per issue) and change it to see
the effect. Action interval is the answer to both "I got spammed" and "I only
got one alert" tickets.

## Exercise 3 — Regression alert

**Rule:**
- When: *The issue changes state from resolved to unresolved*
- Then: notify you

**Trigger:**
1. Resolve the `RecursionError` issue from Exercise 2 in the Sentry UI.
2. `curl http://localhost:5000/api/chaos/recursion`

**Expect:** issue flips back to unresolved, regression alert fires.

**Follow-up:** resolve it as *"resolved in the next release"* instead, bump
`SENTRY_RELEASE` in the compose environment, rebuild, and trigger again from
the new release. Now it is a regression *in a release* — the semantics
customers most often misunderstand.

## Exercise 4 — Metric alert: failure rate

**Rule** (Alerts → Create Alert → Failure Rate):
- Metric: `failure_rate()` on transactions
- Critical: above 10% for 5 minutes

**Trigger:**

```bash
DURATION=600 RPS=4 scripts/chaos-load.sh mixed      # ~20% of requests 500
```

**Expect:** alert enters *warning/critical*, then — this is the part issue
alerts do not have — a **resolved** notification a few minutes after you stop
the load and the rate drops back under threshold. Metric alerts are stateful;
issue alerts are fire-and-forget.

## Exercise 5 — Metric alert: p95 latency

**Rule:**
- Metric: `p95(transaction.duration)`, filtered to the transaction
  `/api/chaos/slow` (practice scoping the alert — an unscoped p95 across the
  whole service is how customers end up with a useless alert)
- Critical: above 2000ms for 5 minutes

**Trigger:**

```bash
DURATION=600 RPS=2 scripts/chaos-load.sh slow       # each request sleeps 3s
```

**Expect:** critical after ~5 minutes, resolves after load stops.

## Exercise 6 — Performance issue: N+1 queries

**Rule:**
- Issue alert on the Python project, condition *a new issue is created*,
  filtered to category *performance* (or reuse Exercise 1's rule).

**Trigger:**

```bash
DURATION=600 RPS=2 scripts/chaos-load.sh nplusone
```

**Expect:** Sentry's N+1 detector needs repeated evidence, not one sample —
expect several minutes of load before an *N+1 Query* performance issue appears.
Open the transaction: 25 identical `select title ...` spans under one request.

**Follow-up:** the db spans are hand-written in `api/app.py`
(`chaos_nplusone`) because sentry-sdk does not auto-instrument psycopg3.
Delete the `start_span` wrappers, redeploy, rerun: endpoint equally slow, but
the trace no longer explains why and no N+1 issue is detected. This is the
"Sentry says my endpoint is slow but shows nothing" ticket.

## Exercise 7 — Crash the service: OOM + downtime

**Trigger:**

```bash
scripts/chaos-load.sh leak       # 50MB leaked per request, 512MB container cap
```

**Expect:** api container OOM-killed within ~10 requests (`docker compose ps`
shows it exited; `restart: "no"` leaves the corpse). Note what Sentry shows:
**nothing**. A SIGKILL gives the SDK no chance to flush. Absence of events is
itself a signal — this is why uptime monitoring exists, and why "no events
since 14:02" tickets are about dead processes, not broken SDKs.

**Uptime monitor:** Sentry's uptime alerts need a publicly reachable URL, so
localhost does not qualify. If you want to practice it, expose the stack with
a tunnel (e.g. `cloudflared tunnel --url http://localhost:5000`), create an
Uptime Monitor against the tunnel URL, then run `leak` and watch the downtime
alert fire. `docker compose up -d api` to revive.

## Exercise 8 — Cron monitor: missed check-in

No code in this repo — cron monitors are about check-ins, not requests.

1. Create a Cron Monitor in Sentry (schedule: every minute or `* * * * *`, grace period 1 minute).
2. On your machine:

   ```bash
   while true; do
     sentry-cli monitors run <monitor-slug> -- curl -s http://localhost:5000/api/categories
     sleep 60
   done
   ```

3. Let it check in green for a few cycles, then Ctrl-C the loop.

**Expect:** a *missed check-in* alert after schedule + grace period. Then make
the wrapped command fail (`-- false`) and compare: *failed* check-in vs
*missed* check-in are different alert conditions.

## Exercise 9 — Spike protection and rate limits

**Trigger:**

```bash
DURATION=120 scripts/chaos-load.sh burst    # ~50 rps of errors
```

**Expect (on a free/dev org):** event counts in Stats stop matching what you
sent. Look for HTTP 429 in SDK debug output (`SENTRY_DEBUG=true`), dropped
events under Stats → Usage, and — if volume is high enough — a spike
protection notification. Learn where *client-side sampling*, *inbound
filters*, *rate limits*, and *spike protection* each drop events; "my event
counts don't add up" tickets are always one of these four.

## Exercise 10 — Frontend alert + distributed trace

**Rule:** on the **React** project, *a new issue is created*.

**Trigger:** open http://localhost:3000/debug-sentry in a browser
(intentional render error), then browse the shop normally.

**Expect:** React error alert with a component stack. Then open any
`pageload` transaction from the browsing session: it should contain the Flask
`/api/...` transaction as a child — that link exists only because of
`tracePropagationTargets` in `ui/src/index.js`. Remove that line and rebuild to
see the traces split.

## Exercise 11 — The alert that doesn't fire (debugging drill)

The most valuable one. Sabotage your own rules, then diagnose from symptoms
only. Do each, wait, explain *why* nothing arrived, fix, verify:

1. Set the rule's environment filter to `production` while the SDK sends
   `environment=docker`.
2. Point the rule at the React project, send errors to the Python project.
3. Set action interval to 24h and trigger the same issue twice.
4. Add a rule condition on a tag the events don't carry (e.g. `service:frontend`).
5. Set `SENTRY_TRACES_SAMPLE_RATE=0.01` in compose and rerun Exercise 5 —
   metric alert data gets sparse. Sampling vs alerting interaction.

Write each diagnosis as a support reply: symptom → what you checked → root
cause → fix → doc link. Keep them; that bank of replies is the real output of
these exercises.

---

## Reset

```bash
docker compose down          # db data is discarded by design
docker compose --env-file ui/.env.local up --build -d
```

Mute or delete alert rules when done practicing — Exercise 2's rule will
happily keep firing every time you run any error scenario.
