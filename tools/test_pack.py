"""Tests for tools/pack.py: what a release contains, the checks and the release file."""
import hashlib
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pack
import sections


def make(root, names, content='x'):
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')


def make_required(out):
    """The pages the blog requires that a test hasn't made, so it sees only the problems it sets up."""
    for page in pack.BLOG_REQUIRES:
        if not (out / page).exists():
            make(out, [page], '<html><head><meta name="description" content="Required."></head><body></body></html>')


class PublishRules(unittest.TestCase):
    def test_only_what_a_browser_needs_and_index_md_pages(self):
        keep = ['index.html', 'js/app.js', 'img/x.png', 'data.json', 'guide/index.md', 'privacy.html']
        drop = ['README.md', 'notes.md', 'card.json', 'section.json', '.gitignore', '.publishignore',
                'build.sh', 'Cargo.toml', 'src/main.rs', 'node_modules/x/index.js', 'package.json', 'yarn.lock']
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            make(folder, keep + drop)
            for name in keep:
                self.assertTrue(pack.publishable(folder, folder / name, []), name)
            for name in drop:
                self.assertFalse(pack.publishable(folder, folder / name, []), name)

    def test_a_publishignore_covers_its_folder_and_below(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / 'site'
            make(site, ['a/.publishignore'], '# checks\n*.mjs\n')
            make(site, ['a/b/check.mjs', 'c/check.mjs'])
            with patch.object(pack, 'SITE', site):
                self.assertTrue(pack.ignored(site / 'a' / 'b' / 'check.mjs'))
                self.assertFalse(pack.ignored(site / 'c' / 'check.mjs'))


class Checks(unittest.TestCase):
    def test_flags_big_files_unwrappable_pages_and_cards_without_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site, out = root / 'site', root / 'dist' / 'projects'
            ok = '<html><head><meta name="description" content="Fine."></head><body></body></html>'
            make(site, ['ok/index.html'], ok)
            make(site, ['missing/card.json'], json.dumps({'title': 'Missing'}))
            make(site, ['away/card.json'], json.dumps({'title': 'Away', 'link': '/projects/games/'}))
            make(site, ['hidden/card.json'], json.dumps({'listed': 'no'}))
            make(out, ['ok/index.html'], ok)
            make(out, ['frag/index.html'], '<p>no document</p>')
            make(out, ['big.png'], 'x' * (pack.MAX_FILE_BYTES + 1))
            make(out, [pack.WRAP_FILE], json.dumps(['ok/index.html', 'frag/index.html', 'gone/index.html']))
            make_required(out)
            with patch.object(pack, 'SITE', site), patch.object(sections, 'SITE', site), patch.object(pack, 'OUT', out):
                errors = pack.check()
        self.assertEqual(len(errors), 4, errors)
        for expected in ('big.png', 'frag/index.html', 'gone/index.html', 'missing'):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_pages_people_land_on_need_a_description(self):
        described = '<html><head><meta name="description" content="What it is."></head><body></body></html>'
        bare = '<html><head><title>Bare</title></head><body></body></html>'
        pages = {
            'index.html': bare,  # the Projects page
            'tool/index.html': described,
            'blank/index.html': '<html><head><meta name="description" content=" "></head><body></body></html>',
            'guide/index.md': '---\ntitle: Guide\ndescription: "A guide."\n---\nText',
            'block/index.html': '---\nlayout: project\nhead: |\n  <title>B</title>\n'
                                '  <meta name="description" content="In the head.">\n---\n<p>x</p>',
            # With a head: block the blog writes no <head> of its own, so this description goes nowhere.
            'unused/index.html': '---\nlayout: project\ndescription: Lost\nhead: |\n  <title>U</title>\n---\n<p>x</p>',
            'moved/index.html': '<html><head><meta http-equiv="refresh" content="0;url=new/"></head><body></body></html>',
            'hidden/index.html': bare,
            '2ndPaste/index.html': bare,
            'plans/index.html': bare,  # a section page
            'plans/one/index.html': bare,
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site, out = root / 'site', root / 'dist' / 'projects'
            for name, text in pages.items():
                make(site, [name], text)
                make(out, [name], text)
            make_required(out)
            make(site, ['hidden/card.json'], json.dumps({'listed': 'no'}))
            make(site, ['away/card.json'], json.dumps({'title': 'Away', 'link': '/projects/games/'}))
            make(site, ['2ndPaste/card.json'], json.dumps({'title': '2ndPaste', 'header': 'no'}))
            make(site, ['plans/section.json'], json.dumps({'title': 'Plans'}))
            with patch.object(pack, 'SITE', site), patch.object(sections, 'SITE', site), patch.object(pack, 'OUT', out):
                errors = pack.check()
        self.assertEqual(sorted(error.split(':')[0] for error in errors),
                         ['blank/index.html', 'index.html', 'plans/index.html', 'plans/one/index.html', 'unused/index.html'])
        self.assertTrue(all('<meta name="description"' in error for error in errors), errors)


class BlogRequires(unittest.TestCase):
    def test_a_pack_without_a_page_the_blog_requires_fails_and_says_why(self):
        page = '<html><head><meta name="description" content="x"></head><body></body></html>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            site, out = root / 'site', root / 'dist' / 'projects'
            site.mkdir(parents=True)
            make(out, [p for p in pack.BLOG_REQUIRES if not p.startswith(('2ndPaste/', 'workouts/'))], page)
            # Jekyll renders an index.md into the index.html the blog asks for.
            make(out, ['workouts/index.md'], '---\ntitle: Workouts\ndescription: x\n---\nText')
            make(out, ['2ndpaste/index.html', '2ndpaste/privacy.html'], page)  # the wrong case
            with patch.object(pack, 'SITE', site), patch.object(sections, 'SITE', site), patch.object(pack, 'OUT', out):
                errors = pack.check()
        why = {'/projects/2ndPaste/index.html': 'App Store Connect',
               '/projects/2ndPaste/privacy.html': 'App Store Connect'}
        self.assertEqual(sorted(error.split(': ')[0] for error in errors), sorted(why), errors)
        for error in errors:
            self.assertIn('the blog requires this page', error)
            self.assertIn(why[error.split(': ')[0]], error)

    def test_the_readme_lists_every_page_the_blog_requires(self):
        readme = (sections.REPO_ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertTrue('\n## What the blog requires\n' in readme,
                        'README.md needs its "What the blog requires" section')
        listed = readme.split('\n## What the blog requires\n', 1)[1].split('\n## ', 1)[0]
        for page in pack.BLOG_REQUIRES:
            self.assertIn('/projects/' + page.removesuffix('index.html'), listed, page)


class Release(unittest.TestCase):
    def test_release_is_reproducible_and_matches_its_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp) / 'dist'
            out = dist / 'projects'
            make(out, ['index.html', 'b/index.html', 'a/img/x.png', pack.WRAP_FILE])
            with patch.object(pack, 'DIST', dist), patch.object(pack, 'OUT', out):
                first = pack.write_release('v1.2.3').read_bytes()
                second = pack.write_release('v1.2.3').read_bytes()
            sha_line = (dist / 'projects-v1.2.3.tar.gz.sha256').read_text(encoding='utf-8')
            with tarfile.open(dist / 'projects-v1.2.3.tar.gz') as tar:
                names = [m.name for m in tar.getmembers()]
        self.assertEqual(first, second)
        self.assertEqual(sha_line, hashlib.sha256(first).hexdigest() + '  projects-v1.2.3.tar.gz\n')
        self.assertEqual(names, [pack.WRAP_FILE, 'a/img/x.png', 'b/index.html', 'index.html'])


if __name__ == '__main__':
    unittest.main()
