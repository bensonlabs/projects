# Projects

Everything under [bensonlabs.org/projects/](https://bensonlabs.org/projects/) except the games:
the Projects page, each project, Workouts and Bootstraps.

- **Owns:** `/projects/` minus `/projects/games/`, which comes from
  [bensonlabs/games](https://github.com/bensonlabs/games). The
  [blog](https://github.com/bensonlabs/blog) assembles the site and owns posts, About and the site
  header.
- **Lifecycle stage:** project. Created 2026-11-07 from the blog's project pages and
  bensonlabs/workouts, history included.
- **Guidance:** `CLAUDE.md` (rules for AI agents, from architectureOS), `tools/sections.py`
  (cards) and `docs/decisions/`.

## Adding something

Tell Claude "add this" with the HTML file (or paste it, or give a link). The `add` skill picks the
section, writes the card, checks it and pushes it to `main`. It's on bensonlabs.org a few minutes
later. Games go to bensonlabs/games instead (its `add-game` skill).

By hand, from anywhere (GitHub's website works, phone included):

1. Add one standalone page (no front matter, no site header) in its section's folder:

   | Section | Folder | Address |
   |---|---|---|
   | Projects | `site/<slug>/index.html` | /projects/<slug>/ |
   | Workouts | `site/workouts/<slug>/index.html` | /projects/workouts/<slug>/ |
   | Bootstraps | `site/bootstraps/<slug>/index.html` | /projects/bootstraps/<slug>/ |

   A write-up can be an `index.md` with front matter instead. A new section is a folder with a
   `section.json` (title, emoji, description, intro).
2. For its card, put a `bl-card` comment at the top of its `<head>` (title, emoji, order,
   description; the fields are in `tools/sections.py`). Without one, the card uses the page's
   `<title>` and description.
3. Give the page a description for search results and link previews:
   `<meta name="description" content="...">` in its `<head>` (the card's description will do; an
   `index.md` takes `description:` in its front matter). Without one the pack fails, and nothing
   is released.
4. Commit it to `main`.

## What the blog requires

The blog's page check refuses a release without any of these pages, and the site keeps the
previous release. `tools/pack.py` fails first, naming the missing page and why, so a removal or a
rename fails here, not days later in the blog:

| Page | Why | From |
|---|---|---|
| /projects/ | Projects in the site menu | `site/index.html` |
| /projects/workouts/ | Workouts in the site menu | `site/workouts/section.json` |
| /projects/bootstraps/ | Bootstraps in the site menu | `site/bootstraps/section.json` |
| /projects/bootstraps/workstations/ | the blog's /bootstraps/ redirects here, and posts link to it | `site/bootstraps/workstations/index.md` |
| /projects/2ndPaste/ and /projects/2ndPaste/privacy.html | registered in App Store Connect | `site/2ndPaste/index.html`, `site/2ndPaste/privacy.html` |
| /projects/tracro/ and /projects/tracro/privacy.html | registered in App Store Connect | `site/tracro/index.html`, `site/tracro/privacy.html` |

The case counts: `2ndPaste`, not `2ndpaste`. Edit these pages in place. To remove, rename or move
one of the first four, change the blog first (its menu, its /bootstraps/ redirect and its page
check). The App Store pages' addresses must never change: keep all four as they are, with their
cards' `header: no`.

## How a change reaches the site

By itself, within a few minutes:

1. A push to `main` runs the Release workflow: it tests the tools, packs everything and compares
   the pack with the latest release. Packs are reproducible, so if nothing the site shows changed,
   it stops there.
2. Otherwise it publishes the next release (`v1.0.3` -> `v1.0.4`): `projects-<version>.tar.gz` and
   its sha256, and asks the blog to publish it.
3. The blog's Update components workflow pins that release in `_data/components.json`, builds the
   whole site with it, runs its page checks and deploys. If a check fails, the site keeps the
   previous release.

## Working on it

- Pack and check everything: `python3 tools/pack.py`
- Preview: `python3 -m http.server -d dist`, then open http://localhost:8000/projects/
- Tests: `python3 -m unittest discover -s tools -p 'test_*.py'`
- On Windows, use `py` where these say `python3`.

## What a release contains

- Everything under `site/`, minus what a browser never needs: Markdown (except `index.md` pages,
  which Jekyll renders), Rust, TOML, TypeScript, shell scripts, lockfiles, package, card and
  metadata files, hidden files, and anything a folder's `.publishignore` lists.
- Every section page with its cards written in: as data for the page's script, and as a plain list
  of links inside `<noscript>` for visitors (and crawlers) without JavaScript.
- `.components-wrap.json`: the pages the blog wraps in the site header (every standalone page
  except cards marked `header: no`).

No published file may be over 750 KB. The Projects page, every section page and the page of
every item with a card need a description (a section page's comes from its `section.json`); the
App Store pages are left as they are. Releases are reproducible: the same files always give the
same sha256.

## What the pages expect from the site

- They're served under `/projects/`, next to `/projects/games/` from bensonlabs/games.
- The site provides `/favicon.svg`, and the `project`, `default` and `post` layouts that pages with
  front matter use.
- Only the pages in `.components-wrap.json` get the site header.
