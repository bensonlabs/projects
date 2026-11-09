"""The docs cite only repo paths that exist: README.md, CLAUDE.md, docs/ and .claude/skills/.

A cited path is a word in `backticks` that starts with tools/, site/, templates/, docs/, .claude/
or .github/; a command counts too (`python3 tools/pack.py` cites tools/pack.py). Only the part
before a placeholder or a wildcard is checked, up to its last slash: `site/workouts/<slug>/`
checks site/workouts/. Fenced code blocks are skipped. Docs are prose, so finding the paths with
a regex is fine here (reading code structure is what needs a parser).
"""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOC_GLOBS = ("README.md", "CLAUDE.md", "docs/**/*.md", ".claude/skills/**/*.md")
PREFIXES = ("tools/", "site/", "templates/", "docs/", ".claude/", ".github/")
FENCE_RE = re.compile(r"^ *(`{3,}|~{3,}).*?^ *\1", re.M | re.S)
CODE_RE = re.compile(r"`([^`]+)`")
VARIABLE_RE = re.compile(r"<[^>]*>|NNNN|[*?{\[]")

# Paths the docs may cite although they aren't in the repo, each with the reason.
ALLOWED = {
    # The kickoff skill (synced from architectureOS) makes worktrees there; git ignores the
    # folder, and it exists only while a worktree does.
    ".claude/worktrees/",
}


def docs() -> list[Path]:
    return sorted({path for pattern in DOC_GLOBS for path in REPO.glob(pattern) if path.is_file()})


def cited_paths(text: str) -> list[str]:
    """The repo paths a doc cites, each cut to its fixed part."""
    found = []
    for span in CODE_RE.findall(FENCE_RE.sub("", text)):
        for word in span.split():
            word = word.strip("'\"()[],;:").rstrip(".")  # a sentence's full stop, not .claude/'s dot
            if not word.startswith(PREFIXES):
                continue
            variable = VARIABLE_RE.search(word)
            if variable:
                word = word[:word.rfind("/", 0, variable.start()) + 1]
            found.append(word)
    return found


class CitedPaths(unittest.TestCase):
    def test_every_path_the_docs_cite_exists(self):
        missing = []
        for doc in docs():
            for path in cited_paths(doc.read_text(encoding="utf-8")):
                if path not in ALLOWED and not (REPO / path).exists():
                    missing.append(f"{doc.relative_to(REPO).as_posix()}: `{path}`")
        self.assertEqual(missing, [], "docs cite paths that don't exist; fix the doc, or add the path "
                                      "to ALLOWED in tools/test_docs.py with the reason")

    def test_every_allowed_path_is_still_cited(self):
        cited = {path for doc in docs() for path in cited_paths(doc.read_text(encoding="utf-8"))}
        self.assertEqual(ALLOWED - cited, set(), "no doc cites these any more: remove them from ALLOWED")

    def test_what_counts_as_a_cited_path(self):
        text = ("Run `python3 tools/pack.py --version v1.2.0`, see `site/<slug>/index.html`, "
                "`docs/decisions/NNNN-<slug>.md`, `tools/test_*.py`, `README.md` and `node x.js`.\n"
                "```bash\ncat docs/not-checked.md\n```\n"
                "Text `site/2ndPaste/index.html`, and `.claude/skills/add/SKILL.md`.\n")
        self.assertEqual(cited_paths(text), ["tools/pack.py", "site/", "docs/decisions/", "tools/",
                                             "site/2ndPaste/index.html", ".claude/skills/add/SKILL.md"])


if __name__ == "__main__":
    unittest.main()
