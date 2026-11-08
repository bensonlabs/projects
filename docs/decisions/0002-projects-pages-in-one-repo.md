# ADR 2: The Projects page, projects, Workouts and Bootstraps in one repo

**Date:** 2026-11-07
**Status:** accepted

## Context

Justin wants to add a project, a workout plan or anything else that is a single HTML page, with
its card on the right index, in one step, for every section in the site menu (2026-11-07). The
project pages lived in the blog and the workout plans in bensonlabs/workouts. Games keep their
own repo, bensonlabs/games (his correction, 2026-11-07).

## Decision

- This repo owns /projects/ except /projects/games/; `site/` mirrors it. The blog's project pages
  and bensonlabs/workouts moved in with their history.
- A section is the Projects page or any folder with a `section.json`; it lists cards for the
  folders inside it (`tools/sections.py`). Workouts and Bootstraps are sections: Justin's plan
  moved to /projects/workouts/justin/ and /projects/workouts/ is the index of plans; the
  Bootstraps post became the first guide at /projects/bootstraps/workstations/.
- The release lists the pages that get the site header, so a new page needs no blog change.
- Every push to `main` that changes what the site shows publishes the next release and asks the
  blog to pin it, like bensonlabs/games.

## Alternatives considered

- One repo with the games too: rejected; games keep their own repo.
- These pages stay in the blog: the blog would build cards itself and mix posts with projects.

## Consequences

- Two content repos (games, projects) with the same packing approach; the blog pins both.
- Two addresses changed (Justin's workout plan, the Bootstraps post); the blog redirects /bootstraps/.
- bensonlabs/workouts is archived.
