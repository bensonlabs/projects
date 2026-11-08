# ADR 4: Bootstraps moves to bensonlabs/bootstraps

**Date:** 2026-11-08
**Status:** accepted (changes ADR 2's Bootstraps section)

## Context

Bootstraps is typed on fresh machines, so it should take as little typing and clicking as
possible. As a section here (ADR 2), the site menu opened /projects/bootstraps/, a page with one
"Workstations" tile to click through. Justin wants bensonlabs.org/bootstraps to show every
bootstrap at once (2026-11-08).

## Decision

- The page moves to bensonlabs/bootstraps, next to the scripts it runs, and is published at
  /bootstraps/ (the blog's ADR 5). Justin chose that over making /projects/bootstraps/ the page.
- This repo keeps a Bootstraps card on the Projects page that links to /bootstraps/ (`link:`, like
  Games), and redirects /projects/bootstraps/ and /projects/bootstraps/workstations/ there. The
  redirects keep the #section of an old link.
- The blog no longer requires the two Bootstraps pages from this repo (README "What the blog
  requires").

## Alternatives considered

- Keep the page here as /projects/bootstraps/ itself: smaller, but the address bar ends at
  /projects/bootstraps/, and the commands live apart from their scripts.

## Consequences

- A bootstrap command changes in bensonlabs/bootstraps, not here; the add skill says so.
- The redirect pages stay as long as old links may be around.
