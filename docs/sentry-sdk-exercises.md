# Sentry SDK & Release Workflow Exercises

Companion to [sentry-alert-exercises.md](./sentry-alert-exercises.md). Those
exercises *receive* signals; these make you *drive* Sentry: sentry-cli,
releases, commits, PRs, source maps, and SDK APIs. Unlike the alert doc, most
of these require you to write code or run CLI commands yourself — the snippets
are starting points, typing and breaking them is the training.

Support relevance: release setup, suspect commits, "Fixes SHORT-ID" resolution,
and source maps are the top of the JS/Python ticket queue.

## Prerequisites

```bash
curl -sL https://sentry.io/get-cli/ | bash    # or: npm i -g @sentry/cli
sentry-cli login                              # creates ~/.sentryclirc with an auth token
sentry-cli info                               # must show your org before continuing
```

Set once per shell (or in `~/.sentryclirc`):

```bash
export SENTRY_ORG=<your-org-slug>
export SENTRY_PROJECT=<python-project-slug>   # switch per exercise
```

---

## Exercise 1 — Release lifecycle with sentry-cli

Releases are what connect events → commits → PRs → "who broke this". Wire the
full lifecycle by hand once so the magic in CI never surprises you.

```bash
REL=$(git rev-parse --short HEAD)

sentry-cli releases new "$REL"
sentry-cli releases set-commits "$REL" --auto      # reads commits from this repo
sentry-cli releases finalize "$REL"
sentry-cli releases deploys "$REL" new -e docker
```

Now make the running stack report that release:

```bash
SENTRY_RELEASE=$REL REACT_APP_SENTRY_RELEASE=$REL \
  docker compose --env-file ui/.env.local up --build -d
curl http://localhost:5000/api/debug-sentry
```

**Verify:** the new event's `release` tag is your SHA; the release page in
Sentry lists your commits and the deploy. Then answer from the UI alone:
what is the difference between an *unfinalized* and *finalized* release?
(Hint: `date created` vs `date released` — customers ask this.)

`--auto` requires the repo to be connected in Sentry (Settings →
Integrations → GitHub, add `sojay/docker-builds`). Without it you get
`could not find repository` — trigger that error once on purpose, it is a
classic ticket.

## Exercise 2 — Suspect commits

1. On a branch, introduce an obvious bug in a **new commit**, e.g. in
   `api/app.py` `get_categories`:

   ```python
   return jsonify(mock_categories[99])   # IndexError
   ```

2. Repeat Exercise 1's release steps with the new SHA, rebuild, then
   `curl http://localhost:5000/api/categories`.

**Verify:** the new `IndexError` issue shows a **Suspect Commits** section
naming your commit and you as suspect. Understand the inputs Sentry needs
for this: (a) release with commits, (b) the file path in the stack trace
matching a path in the commit. Break (b) on purpose — the api runs in
`/app/app.py` inside the container while the repo says `api/app.py` — and
fix it with Settings → your project → **stack trace linking / code mappings**.
Path-mapping mismatches are a constant support theme.

Revert the bug commit when done (`git revert`), keep it in history — you
want a "fix commit" for Exercise 3.

## Exercise 3 — Resolve via commit and PR

The `Fixes <SHORT-ID>` workflow. Requires the GitHub integration from
Exercise 1.

1. Take the `IndexError` issue's short ID from its page (e.g.
   `BOOKSTORE-API-42`).
2. Open a PR for your revert branch. Put `Fixes BOOKSTORE-API-42` in the PR
   description (or in the commit message).
3. Merge the PR.

**Verify:**
- The Sentry issue moves to **resolved in commit** (or *resolved in release*
  once a release containing the commit is created).
- The issue's activity log shows the PR link; the PR shows Sentry's
  annotation.
- Now trigger the error again from the **old** release: no regression alert.
  Trigger it from a **newer** release than the fix: regression. Reason about
  why — this "resolved in release" semantic ordering is one of the most
  misunderstood behaviors in support tickets.

## Exercise 4 — Source maps

The single highest-volume JS support topic. Do it broken-first.

1. **Broken:** open http://localhost:3000/debug-sentry (prod build, minified).
   Look at the event: one-letter function names, `main.a1b2c3.js` frames.
   This is what every "my stack traces are unreadable" ticket looks like.
2. **Fix locally:**

   ```bash
   cd ui
   REL=$(git rev-parse --short HEAD)
   REACT_APP_SENTRY_RELEASE=$REL npm run build
   npx @sentry/cli sourcemaps inject build          # stamps debug IDs
   SENTRY_PROJECT=<react-project-slug> npx @sentry/cli sourcemaps upload --release="$REL" build
   ```

   Serve that exact build (simplest: temporarily `COPY build /usr/share/...`
   or `npx serve -s build`), trigger the error again.
3. **Verify:** readable frames pointing at `DebugSentry.js`.
4. **Diagnose like support:** re-break it three ways and run
   `npx @sentry/cli sourcemaps explain <event-id>` after each —
   (a) upload maps for the wrong release, (b) skip the `inject` step,
   (c) rebuild after uploading (new bundle hashes, stale artifacts).
   Learn which symptom each produces.

## Exercise 5 — SDK enrichment: user, tags, breadcrumbs

In `api/app.py`'s `enrich_sentry_scope` (there is already a `set_tag` there),
add:

```python
sentry_sdk.set_user({"id": request.headers.get("X-Demo-User", "anonymous")})
sentry_sdk.add_breadcrumb(category="request", message=f"handling {request.path}")
```

Trigger errors with `curl -H 'X-Demo-User: worker-7' .../api/chaos/recursion`.

**Verify:** issue shows the user, `user.id:worker-7` works as a search query,
"number of users affected" starts counting. Then check what
`send_default_pii=false` (the current setting) strips vs what your explicit
`set_user` sends anyway — explicit beats the PII default, which surprises
customers doing privacy reviews.

## Exercise 6 — Fix bad grouping with fingerprints

`api/app.py` already contains a grouping bug you diagnosed in training:

```python
sentry_sdk.capture_message(f"Product not found: {product_id}", level="warning")
```

1. Enable it (`SENTRY_CAPTURE_404S=true` — already on in compose) and hit
   `/api/products/900`, `/api/products/901`, ... — one issue **per id**.
2. Fix with a fingerprint:

   ```python
   with sentry_sdk.new_scope() as scope:
       scope.fingerprint = ["product-not-found"]
       sentry_sdk.capture_message(f"Product not found: {product_id}", level="warning")
   ```

3. Redeploy, hit several ids again: one issue, ids visible per-event.

**Follow-up:** the old per-id issues are still there — practice **merging**
them in the UI, then unmerging one. Customers who already shipped the bad
pattern need merge, not a code fix.

## Exercise 7 — `before_send`: drop and scrub in the SDK

Add to `sentry_sdk.init` in `api/app.py`:

```python
def before_send(event, hint):
    # drop the 404 warnings entirely
    if event.get("logentry", {}).get("message", "").startswith("Product not found"):
        return None
    # scrub a header
    headers = event.get("request", {}).get("headers", {})
    headers.pop("X-Demo-User", None)
    return event
```

**Verify:** 404 messages stop arriving; errors still do, minus the header.
Then compare against doing the same with server-side **inbound filters**:
where does each drop the event, and which one still consumes quota?
(`before_send` drops client-side before send; inbound filters drop at ingest —
the stats page shows the difference.)

## Exercise 8 — Profiling the N+1

In `sentry_sdk.init` add:

```python
profiles_sample_rate=1.0,
```

Redeploy, run `DURATION=120 scripts/chaos-load.sh nplusone`, open a
`/api/chaos/nplusone` transaction → profile/flame graph.

**Verify:** the flame graph shows time inside psycopg calls — evidence at a
level below spans. Useful contrast with alert-exercise 6, where deleting the
manual spans blinded the trace: the profile still sees it.

## Exercise 9 — Crash the SDK's delivery, watch it recover

```bash
# point the api at a black-hole DSN
SENTRY_DSN=https://x@localhost:9/1 docker compose up -d api
docker compose logs -f api   # with SENTRY_DEBUG handling: add debug=True to init
```

Trigger errors. **Verify:** app keeps serving 200s/500s normally — SDK
failures are never allowed to break the host app (a design guarantee
customers ask about). Restore the real DSN, confirm delivery resumes.
While here: read what the SDK logs on retry/backoff; that log output is what
you will ask customers to capture.

---

## Order of operations

1 → 2 → 3 is one storyline (release → suspect commit → PR fix) and needs the
GitHub integration; do it in one sitting. 4 is standalone. 5–8 are code
exercises on this repo; commit each on a branch so the release/PR machinery
from 1–3 keeps having material to work with.
