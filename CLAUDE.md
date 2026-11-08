# Projects: instructions for AI agents

<!-- Only the governance blocks below come from architectureOS; /sync-governance updates them. Everything outside them belongs to this project and is never changed by a sync. -->

<!-- BEGIN governance:scaffold -->
## How this file works

- **Personal preferences** of the person you're working with come from their own Claude settings
  (their user-level `~/.claude/CLAUDE.md`), never from this file.
- **Core rules** and **conventions** (the next two blocks) come from the architectureOS repo and are
  the same in every project built from it. To change one, change it there (core rule 12).
- **Core rules not used here** (in the project rules) lists any core rule this project can't use,
  with the reason. Skip only those, and only while the reason holds. A rule that seems not to fit
  but isn't listed still applies: ask the person rather than skip it.
- **Project rules** (at the bottom) belong to this project. Write each one in three parts: when it
  fires (a table of triggers), how to do it (files, commands), and a decision shortcut for the
  usual edge cases. Give non-obvious rules a date and who decided ("owner decision, 2026-11-07").
- **Background:** each rule names a doc in the architectureOS repo (`source_repo` in
  `.governance-sync.json`). It's private; read a doc with
  `gh api repos/<owner>/<repo>/contents/docs/<name>.md -H "Accept: application/vnd.github.raw"`.
<!-- END governance:scaffold -->

<!-- BEGIN governance:core-rules -->
## Core rules

### 1. Check what exists before building new surface

- **Fires on:** a new page or route, screen, top-level command, permission or role, or menu entry.
  **Not on:** a bug fix, a refactor, or a column, filter or action on an existing page.
- **Do:** run the `feature-fit` skill before building. Write down the need, search what already
  exists, show the person a fit matrix and a verdict (use as-is, extend, or new), and save a
  one-page note in `docs/feature-fit/` that names what it adds. The person decides. Two reminders
  catch what you miss: one while you write, one at push (what counts is set in
  `.claude/hooks/reminders.config.json`).
- **Shortcut:** people can already do it in a few steps → document how, don't build. It's an
  existing page's job with one more column, filter or action → extend that page. Otherwise build
  new, and say why in one sentence.
- Doc: `check-before-building.md`.

### 2. Docs change in the same commit as the code they describe

- **Fires on:** a change to what people do or see, a business rule, a permission, an endpoint, a
  data field, or a tracked status.
- **Do:** update the help, starter doc, ledger or decision record that describes it in the same
  commit, so undoing the commit undoes both. If nothing needs updating, say so with a line in the
  commit message: `Docs-Impact: none - <why>`.
- Doc: `same-commit.md`.

### 3. Answer a reminder with a reason a reviewer can read

- **Fires on:** a reminder (a hook, a check, a skill step) that applies to your change, when you
  decide no action is needed.
- **Do:** add a line at the end of the commit message, `<Check>: none - <reason>`, for example
  `Feature-Fit: none - settings screen, not a new feature` or `Docs-Impact: none - styling only`.
  Write the reason for a reviewer. Never skip hooks (`--no-verify`) instead.
- Doc: `commit-trailers.md`.

### 4. Cite where behavior comes from

- **Fires on:** code that implements a requirement from somewhere else: a spec, an issue, a system
  being replaced, a person's decision.
- **Do:** name the source in a comment next to it: `// Source: <reference>` (a spec section, an
  issue, `oldapp/orders.py:120-140`, "owner decision, 2026-11-04"). A file that ports one source
  file says so at the top: `// Source-File: <path>`.
- Doc: `provenance-markers.md`.

### 5. Don't invent rules

- **Fires on:** adding a validation, a permission check, a status rule, a limit or a default.
- **Do:** every one traces to a source (rule 4). If one is genuinely needed but has no source, mark
  it `// invented: <why>` and list it in the PR for a person to approve. Before changing code to
  match a doc, check the doc against the source: docs go stale.
- Doc: `no-invented-rules.md`.

### 6. Trust order when sources disagree

The source itself (the running system, the spec, the authoritative data file) wins, then current
code, then docs and ledgers, then memory of past sessions. Fix the lower one to match the higher
one. Fix stale docs you come across while working in that area, in the same commit; don't start a
mass rewrite. Before recommending a file, function or flag you remember, check it still exists.
Doc: `trust-order.md`.

### 7. Record non-obvious decisions

- **Fires on:** a choice a reasonable person could have made the other way, one that is expensive
  to reverse, or one that makes code look surprising.
- **Do:** add `docs/decisions/NNNN-<slug>.md` from `docs/decisions/TEMPLATE.md`. Reversing a
  decision means a new record that supersedes the old one; never edit the old one.
- Doc: `decision-records.md`.

### 8. Analyze code structure with a parser, not text matching

- **Fires on:** a script, audit or codemod that decides something from code structure (what calls
  what, which attributes a class has, which routes exist).
- **Do:** use the language's parser or compiler API (TypeScript compiler API, Roslyn, Python
  `ast`). Regex and string search are fine for logs, prose, non-code files, reminders that only
  nudge, and narrowing down which files to parse, never for the final decision.
- Doc: `analyze-with-a-parser.md`.

### 9. Access is enforced on the server, and widened only with a source

- **Fires on:** a permission check, a role, a sharing or visibility rule, an endpoint that reads or
  changes data, or anything else that changes who can see or do what.
- **Do:**
  - Check access on the server, against the stored record (whose it is, who it's shared with),
    never against an ID, role or owner sent in the request. Checks in the browser only decide what
    to show.
  - Never run SQL or a query built from request text: accept IDs and structured filters.
  - Widening access (more people, more records, fewer checks) cites its source (rule 4) and is
    listed in the PR for the owner to approve. Never undo a security fix to make something work.
- Doc: `access-on-the-server.md`.

### 10. Report each work state as its own fact

- **Fires on:** saying where a change stands: in a report, a PR, a handoff note, an issue.
- **Do:** keep the states apart: **implemented** (the change exists), **verified** (the stated
  check ran and passed, and you saw the result), **accepted** (the person approved it), **merged**
  (it's on the target branch), **released** (users or the target environment have it). Never infer
  a later state from an earlier one: a passing build isn't a release, and a check that didn't run
  didn't pass.
- Doc: `work-states.md`.

### 11. Protect user data before changing it destructively

- **Fires on:** a migration, bulk edit, import, cleanup, or anything else that deletes or rewrites
  data people created.
- **Do:** export it first, check the export is complete, and prove the restore works somewhere
  disposable. Check inputs before changing anything, and make the change all-or-nothing so a
  failure leaves no partial state. Ask the person before running it on real data.
- Doc: `user-data-safety.md`.

### 12. Keep governance in step with architectureOS

Run `/sync-governance` now and then; it updates the governance blocks, skills, hooks and
templates. To improve a core rule, a skill or a template, change it in the architectureOS repo so
every project gets it, not only here. Doc: `keeping-projects-in-sync.md`.
<!-- END governance:core-rules -->

<!-- BEGIN governance:conventions -->
## Conventions

- **Every project states its lifecycle stage**: experiment, project, maintained, product or
  archived (in the project rules and the README). An experiment is labeled as one and makes no
  production claims. Moving up a stage is a decision the person makes, not a reward for
  accumulating code; a stage brings only the controls its risk needs.
- **Boring, replaceable technology.** Prefer what the next person can understand, run and replace.
  No shared infrastructure, service or library until a second real user of it exists. Settle who
  owns a piece of data or behavior before splitting it into another service or repo.
- **Every repo's README** says what the repo owns, its lifecycle stage, how to run or use it, and
  where its guidance lives.
- **Small, reversible steps.** Prefer a reviewable increment with a way back over a sweeping
  change; keep existing users of a thing working until its replacement is proven.
- **Never start or re-run a deploy or CI workflow** without an explicit go for that run. When asked
  whether something is reachable or allowed, check with read-only calls and run nothing.
- **Test data in a sandbox** (an environment the project rules name as safe for testing) is fine
  without asking: label test records TEST, and say afterwards what was done. Anything shared or
  live goes through the person first.
- **People's data stays where it lives.** Users' personal data never goes into commits, PR
  descriptions, issues, logs, test data or screenshots, nor into any service the project doesn't
  already trust with it. Logs mask identifying values.
- **Secrets never go in git.** Passwords, keys, tokens and connection strings stay in the
  environment or a secrets store; committed config holds placeholders. If one is committed, tell
  the person at once: rotating it matters more than rewriting history.
- **Sample data is invented.** Mockups, demo data and fixtures use made-up people and places,
  checked against real records for accidental matches.

Doc (where each convention came from): `conventions.md`.
<!-- END governance:conventions -->

## Project rules

### About this project

- What it owns: everything under bensonlabs.org/projects/ except the games: the Projects page,
  each project, Workouts and Bootstraps. `site/` mirrors that address. The games come from
  bensonlabs/games (into /projects/games/); the blog (bensonlabs/blog) assembles the site and owns
  posts, About and the site header.
- Lifecycle stage (experiment, project, maintained, product, archived): project. Created
  2026-11-07 from the blog's project pages and bensonlabs/workouts, history included (ADR 2).

### Core rules not used here

- 1 (check what exists before building new surface): adding pages is what this repo is for.
- 4 (cite where behavior comes from): the pages implement no outside spec.
- 5 (don't invent rules): a page's limits and defaults are design choices, not rules that need a source.
- 9 (access on the server): static files; there is no server.

Rule 11 still applies: some pages keep data in the visitor's browser (see Pages and cards).

### Pages and cards

| When | Do |
|---|---|
| Adding or changing anything | Use the `add` skill: it picks the section, writes the card, checks and pushes straight to `main`; it goes live by itself. |
| A card | `card.json`, `section.json` or a `bl-card` comment; the fields are in `tools/sections.py`. A card with `link:` leads elsewhere (Games). |
| A new section | A folder with a `section.json` (title, emoji, description, intro); its page comes from `templates/section.html`. A section with its own `index.html` needs both placeholders that `tools/sections.py` fills in: the cards for its script and the links inside `<noscript>`. |
| A page's description | The Projects page, every section page and the page of every item with a card need one: `<meta name="description" content="...">` in the `<head>` (the card's description will do), `description:` in an `index.md`'s front matter, or a section's `section.json` description. `tools/pack.py` refuses a pack without it. |
| Changing how a page stores data in the browser (core rule 11) | Keep existing data loading: read the old format or migrate it. Never silently reset what a visitor saved. |
| Images, sounds, fonts | No published file may be over 750 KB: size images to how they're drawn. |
| Removing, moving or renaming a page | Moving or renaming changes its address: say so. The pages in README "What the blog requires" (the site menu's Projects, Workouts and Bootstraps pages, the Workstations guide the blog's /bootstraps/ redirects to, the App Store pages) stay: `tools/pack.py` and the blog's page check refuse a release without them. Removing or moving one needs the blog changed first; tell the person and stop. |
| 2ndPaste's or Tracro's support or privacy page | App Store Connect has their URLs. Edit them in place, but never move, rename or remove `site/2ndPaste/index.html`, `site/2ndPaste/privacy.html`, `site/tracro/index.html` or `site/tracro/privacy.html` (the case counts), and keep their cards' `header: no`. `tools/pack.py` and the blog's page check refuse a release without them. |

Shortcut: if `python3 tools/pack.py` passes, the release will build.

### Files shared with bensonlabs/games

- `tools/next_version.py` and `tools/html_checks.py` are identical in both repos, and so are three
  functions in `tools/pack.py` (`read_publishignore`, `publishable`, `write_release`).
  `.github/workflows/release.yml` and `ci.yml` differ only in the lines marked "games only" and
  their names. Each says so at its top. Change one, and make the same change in the other repo.
- Why two copies rather than a shared package: the repos are small and separate on purpose (site
  review P11, owner default 2026-11-08).

### Commands

- Install: nothing.
- Run locally: `python3 tools/pack.py`, then `python3 -m http.server -d dist` and open
  http://localhost:8000/projects/ (the site header and Jekyll pages appear only on the real site).
- Tests, type check, lint (wrap-up runs these): `python3 -m unittest discover -s tools -p 'test_*.py'`,
  `python3 tools/pack.py`.
- Push reminder, once per clone: `node .claude/hooks/push-reminder.mjs --install`
- On Windows, use `py` where these say `python3` (`python3` isn't on the PATH there).

### Environments

- Sandbox for testing: a local pack in `dist/`. There is no shared test site.
- Live, and who changes it: bensonlabs.org shows the release pinned in the blog's
  `_data/components.json`. A push to `main` that changes what the site shows goes live within
  minutes; the blog deploys only after its own checks pass.

### Branches, review and release

- PRs go to (target branch): `main`. Adding, changing or removing a page goes straight to `main`
  (owner decision, 2026-11-07); tools and workflows go through a PR.
- Branch names (default `feature/<short-name>`): the default.
- Bring a branch up to date by (merge or rebase): merge.
- Reviewer: with no second reviewer, the person reviews the whole diff themselves before it merges.
- How changes reach users, and who runs it: nobody runs anything. Every push to `main` that changes
  what the site shows makes the Release workflow publish the next version
  (`projects-vX.Y.Z.tar.gz` and its sha256) and ask the blog to pin it; the blog's Update
  components workflow runs its checks, pins the release and deploys.

### Where things live (feature-fit searches these)

- Pages and navigation: `site/` mirrors /projects/: a folder per project in `site/`, per plan in
  `site/workouts/`, per guide in `site/bootstraps/`; cards as above. Site navigation belongs to the blog.
- Help or user docs: `README.md`; `tools/sections.py` (cards).
- Starter docs: none yet.
- API endpoints: none; the pages are static files.

### Commit-message answers this project uses

- `Feature-Fit: none - <reason>` and `Docs-Impact: none - <reason>` (core rules 1 to 3).
