---
name: add
description: Add anything to bensonlabs.org/projects/ - a project, a workout plan, a bootstrap guide, or a new section - from one HTML file (or a Markdown write-up): put it in the right folder, write its card, check it and push; it goes live by itself within minutes. Use whenever Justin hands over a page and wants it on the site, or asks to change, move or remove one, or its card.
---

# Add something to the site

Adding is one push to `main`: the Release workflow publishes the next release and the blog pins
it and deploys after its checks (owner decision, 2026-11-08). Do the steps below without asking,
except where they say to show Justin something.

1. **Get the page.** An HTML file, pasted HTML, or a link to download; a write-up can be Markdown
   (`index.md` with front matter, which Jekyll renders). An HTML page must be one complete,
   standalone document: its own `<html>`, `<head>` and `<body>`, no front matter, no site header
   (`docs/AGENT_PROMPT_ADDENDUM.md`). If it loads other files, bring them into the same folder and
   keep their relative paths. Keep every file under 750 KB: shrink images to the size they're drawn.
   It needs a description for search results and link previews: a
   `<meta name="description" content="...">` in its `<head>` (in an `index.md`, `description:` in
   its front matter). If it has none, give it the card's description (step 3).
2. **Pick the section** from what it is (ask only if it could be either):

   | It is | It goes in | Address |
   |---|---|---|
   | a game | not here: bensonlabs/games (its `add-game` skill) | /projects/games/<slug>/ |
   | a workout plan | `site/workouts/<slug>/` | /projects/workouts/<slug>/ |
   | a bootstrap guide | `site/bootstraps/<slug>/` | /projects/bootstraps/<slug>/ |
   | a project, a tool, anything else | `site/<slug>/` | /projects/<slug>/ (a card on the Projects page) |
   | a new kind of thing | a new folder with a `section.json` (title, emoji, description, intro) | its own index page, with a card on the Projects page |

   The slug is short, lowercase, words joined by hyphens, from the title. Make sure the folder
   doesn't exist yet.
3. **Write the card** (`tools/sections.py` explains every field). In an HTML page, a comment at the
   top of `<head>`:

   ```html
   <!-- bl-card
   title: Its Title
   emoji: 🎮
   order: 999
   description: One sentence on what it is or what you do with it. Made by <model> in <tool>.
   -->
   ```

   In an `index.md`, put the same fields in its front matter.
   Optional: `cta:` (the button's words, "Open →" by default), `link:` (a card that leads
   somewhere else), `header: no` (the page stays standalone, without the site header),
   `listed: no` (no card). Pick an emoji that fits; write the description from the page itself; end
   it with "Made by <model> in <tool>." only when Justin says or the file shows. Keep `order: 999`
   unless he gives a place. Show him the card in one line; change it if he asks.
4. **Check it**: `python3 tools/pack.py` must pass. It catches a page that can't get the site header,
   a card leading nowhere, a page with a card but no description, and files over 750 KB.
5. **Commit and push** only that folder: `git add site/<path>`, a commit "Add <title>", and
   `git push` to `main`. If the push reminder says something, answer it in the commit message as it
   asks.
6. **Confirm it went live.** Watch the newest Release run (`gh run watch`), then the blog's Update
   components run. When both pass, check the page answers 200 and its section page shows the card.
   Report the link. If a check fails, the site keeps the previous release: say what failed.

## Changing, moving or removing

Same steps from 3. Edit the page or its card, or move or delete its folder; commit "Change …",
"Move …" or "Remove …", and push. Moving changes the address: say so.

Never move, rename or remove 2ndPaste's or Tracro's support and privacy pages
(`site/2ndPaste/index.html` and `privacy.html`, `site/tracro/index.html` and `privacy.html`):
their URLs are registered in App Store Connect, and the blog refuses a release without them.
Edit them in place. If Justin asks to move one, first tell him the App Store URLs would break.
