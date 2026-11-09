# Projects: instructions for AI agents

<!-- Only the governance blocks below come from architectureOS; /sync-governance updates them. Everything outside them belongs to this project and is never changed by a sync. -->

<!-- BEGIN governance:scaffold -->
## How this file works

- **Personal preferences** come from the person's own `~/.claude/CLAUDE.md`, never from this file.
- **Core rules** (the next block) come from the architectureOS repo and are the same in every
  project. To change one, change it there; `/sync-governance` keeps this file in step.
- **Project rules** (at the bottom) belong to this project: what it owns, its commands, what must
  never move, and its own checks. Give a non-obvious one a date and who decided ("owner decision,
  2026-11-07").
- **Apps with users** add the product rules (architectureOS doc `product-rules.md`) to their
  project rules when they reach the "product" stage.
- **Background:** each core rule names a doc in the architectureOS repo (`source_repo` in
  `.governance-sync.json`). It's private; read a doc with
  `gh api repos/<owner>/<repo>/contents/docs/<name>.md -H "Accept: application/vnd.github.raw"`.
<!-- END governance:scaffold -->

<!-- BEGIN governance:core-rules -->
## Core rules

1. **Record decisions that aren't obvious.** A choice someone could reasonably have made the other
   way, or one that's costly to undo, gets `docs/decisions/NNNN-<slug>.md` from `TEMPLATE.md`.
   Reversing one is a new record that supersedes it; the old one gets only a "superseded by" line.
   Doc: `decision-records.md`.
2. **Docs change in the same commit as the code they describe,** so undoing the commit undoes both.
   When code, docs and memory disagree, the source wins (the running system, the spec, the data),
   then the code, then the docs: fix the lower one while you're there.
   Docs: `same-commit.md`, `trust-order.md`.
3. **Report each work state as its own fact:** built, checked (the check ran and passed, and you saw
   it), approved, merged, live. Never infer a later state from an earlier one.
   Doc: `work-states.md`.
4. **Never start or re-run a deploy or CI run without a go for that run.** A go to merge isn't a go
   to start a run. To find out whether something is reachable or allowed, use read-only calls.
   Doc: `conventions.md`.
5. **Secrets and people's data never go in git:** not in code, commits, PRs, issues, logs, test data
   or screenshots. Committed config holds placeholders. If one slips in, tell the person at once.
   Doc: `conventions.md`.
6. **A mistake that happens twice becomes a check that fails.** Mechanical facts (a path exists,
   copies match, a page is published) get a test or CI check, not a reminder. Judgment calls stay
   with people. Doc: `checks-over-reminders.md`.
<!-- END governance:core-rules -->

## Project rules

### About this project

- What it owns: everything under bensonlabs.org/projects/ except the games: the Projects page,
  each project and Workouts. `site/` mirrors that address. Bootstraps lives in bensonlabs/bootstraps
  (bensonlabs.org/bootstraps/, ADR 4); here it's only a link card and redirects from its old addresses. The games come from
  bensonlabs/games (into /projects/games/); the blog (bensonlabs/blog) assembles the site and owns
  posts, About and the site header.
- Lifecycle stage (experiment, project, maintained, product, archived): project. Created
  2026-11-07 from the blog's project pages and bensonlabs/workouts, history included (ADR 2).

### Pages and cards

| When | Do |
|---|---|
| Adding or changing anything | Use the `add` skill: it picks the section, writes the card, checks and pushes straight to `main`; it goes live by itself. |
| A card | `card.json`, `section.json` or a `bl-card` comment; the fields are in `tools/sections.py`. A card with `link:` leads elsewhere (Games). |
| A new section | A folder with a `section.json` (title, emoji, description, intro); its page comes from `templates/section.html`. A section with its own `index.html` needs both placeholders that `tools/sections.py` fills in: the cards for its script and the links inside `<noscript>`. |
| A page's description | The Projects page, every section page and the page of every item with a card need one: `<meta name="description" content="...">` in the `<head>` (the card's description will do), `description:` in an `index.md`'s front matter, or a section's `section.json` description. `tools/pack.py` refuses a pack without it. |
| Changing how a page stores data in the browser | Keep existing data loading: read the old format or migrate it. Never silently reset what a visitor saved. |
| Images, sounds, fonts | No published file may be over 750 KB: size images to how they're drawn. |
| Removing, moving or renaming a page | Moving or renaming changes its address: say so. The pages in README "What the blog requires" (the site menu's Projects and Workouts pages, the App Store pages) stay: `tools/pack.py` and the blog's page check refuse a release without them. Removing or moving one needs the blog changed first; tell the person and stop. |
| 2ndPaste's or Tracro's support or privacy page | App Store Connect has their URLs. Edit them in place, but never move, rename or remove `site/2ndPaste/index.html`, `site/2ndPaste/privacy.html`, `site/tracro/index.html` or `site/tracro/privacy.html` (the case counts), and keep their cards' `header: no`. `tools/pack.py` and the blog's page check refuse a release without them. |

Shortcut: if `python3 tools/pack.py` passes, the release will build.

### Files shared with other repos

- Identical in bensonlabs/games, bensonlabs/projects and bensonlabs/bootstraps:
  `.github/workflows/release.yml`, `tools/next_version.py`, `tools/check_shared.py`,
  `tools/test_check_shared.py`, and three functions in `tools/pack.py` (`read_publishignore`,
  `publishable`, `write_release`).
- Identical in games and projects: `.github/workflows/ci.yml` and `tools/html_checks.py`.
- What differs per repo comes from the repository's name (`github.event.repository.name`): the
  component, its release notes, and the steps that have an `if:` for games. Keep it that way: no
  per-repo edits inside a shared file.
- `tools/check_shared.py` runs on every pull request and fails when a copy differs; its list of
  shared files is at its top. To change a shared file, make the same change in every repo that
  shares it on one branch name, push all those branches, then open the pull requests: each check
  compares against the other repos' branch of that name, or main if there's none.
- Why copies rather than a shared package: the repos are small and separate on purpose (site
  review P11, owner default 2026-11-08). The check replaced "change both" notes in the files
  (owner decision 2026-11-08: checks, not reminders).

### Commands

- Install: nothing.
- Run locally: `python3 tools/pack.py`, then `python3 -m http.server -d dist` and open
  http://localhost:8000/projects/ (the site header and Jekyll pages appear only on the real site).
- Tests, type check, lint (wrap-up runs these): `python3 -m unittest discover -s tools -p 'test_*.py'`,
  `python3 tools/pack.py`.
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

### Checks this project relies on

Each stops a mistake that happened once or would break the site (core rule 6):

- `tools/pack.py` refuses a pack when a page the blog requires is missing (README "What the blog
  requires", including the four App Store pages), a card leads to a page that isn't packed, a page
  listed for the site header isn't a whole document, or a file is over 750 KB.
- `tools/test_docs.py`: every repo path the docs cite in backticks exists.
- `tools/check_shared.py` (pull request job "Shared files match the other repos"): the files shared
  with bensonlabs/games and bensonlabs/bootstraps match their copies.
- actionlint (pull request job "Lint the workflows"): the workflow files are valid, and their
  scripts pass shellcheck.
- The release publishes only main's current head (ADR 3), and the blog deploys a release only
  after its own page checks pass, including the App Store pages.

### Where things live

- Pages and navigation: `site/` mirrors /projects/: a folder per project in `site/`, per plan in
  `site/workouts/`; cards as above. `site/bootstraps/` only redirects to /bootstraps/ (bensonlabs/bootstraps). Site navigation belongs to the blog.
- Help or user docs: `README.md`; `tools/sections.py` (cards).
- Starter docs: none yet.
- API endpoints: none; the pages are static files.
