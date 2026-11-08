# ADR 3: Release only main's head, from a separate publish job

**Date:** 2026-11-08
**Status:** accepted

## Context

The site review on 2026-11-08 found that the Release workflow could publish the wrong thing:

- Started by hand on another branch, it released that branch to the live site, without a review.
- Re-running an old run (for example after renewing an expired token) released that run's older
  content as the newest version, and the blog deployed it.
- Without `pipefail`, a failed sha256 download looked like "no release yet", so the same pack was
  published again as a new version.

bensonlabs/games had the same workflow, with one more risk: its single job ran npm packages while
it held the write token and the blog's dispatch token. Justin approved the fixes the same morning.

## Decision

- The same workflow as bensonlabs/games (its ADR 4), so `.github/workflows/release.yml` stays
  shared: change both.
- Two jobs. **build** tests and packs with read-only access. **publish** downloads the pack and
  releases it. It holds `contents: write` and `BLOG_DISPATCH_TOKEN`, and runs only this repo's own
  Python and `gh`.
- Only main is released (`if:` on the build job). The publish job also checks that the run's
  commit is still main's head, so an old or re-run run publishes nothing.
- The publish job runs in the `release` environment, which only main may use. When the token is
  next renewed, saving it there instead of as a repository secret keeps it from every other job
  and branch.
- The scripts run with `pipefail`. The job fails when a release exists but its sha256 can't be
  read, and when the blog refuses the token, with a message saying the release is out and the
  blog's daily run pins it.
- The blog is asked to update every component to its newest release, so a request that replaces
  one still queued in the blog loses nothing.

## Alternatives considered

- Keep one job here, since nothing in this repo installs packages: the two repos' workflows would
  drift apart, and a package added later would run beside the tokens.

## Consequences

- A release takes one more job (about 15 s) to hand the pack over.
- Re-running a failed old run is safe; it publishes nothing unless its commit is still main's head.
- Each release shows as a deployment to the `release` environment on the repo page.
