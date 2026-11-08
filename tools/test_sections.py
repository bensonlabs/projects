"""Tests for tools/sections.py: where cards come from, section pages, and which pages get the site header."""
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

import sections
from html_checks import Page

TEMPLATE = '<html><head><title>__SECTION_TITLE__</title><meta name="description" content="__SECTION_DESCRIPTION__"></head><body><p>__SECTION_INTRO__</p><noscript>' + sections.NOSCRIPT_PLACEHOLDER + '</noscript><script>const GAMES = ' + sections.PLACEHOLDER + ';</script></body></html>'


class Links(HTMLParser):
    """The links on a page as [href, text, inside <noscript>], the text inside <noscript>, and the
    script's text."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.noscript = 0
        self.link = None
        self.links = []
        self.noscript_text = ''
        self.script = False
        self.script_text = ''
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.script = tag == 'script'
        if tag == 'noscript':
            self.noscript += 1
        elif tag == 'a':
            self.link = [dict(attrs).get('href'), '', self.noscript > 0]
            self.links.append(self.link)

    def handle_endtag(self, tag):
        self.script = False
        if tag == 'noscript':
            self.noscript -= 1
        elif tag == 'a':
            self.link = None

    def handle_data(self, data):
        if self.script:
            self.script_text += data
        if self.link is not None:
            self.link[1] += data
        if self.noscript:
            self.noscript_text += data


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


class Cards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.site = Path(self.tmp.name) / 'site'
        self.site.mkdir()
        write(Path(self.tmp.name), 'templates/section.html', TEMPLATE)
        self.patches = [patch.object(sections, 'SITE', self.site),
                        patch.object(sections, 'TEMPLATE', Path(self.tmp.name) / 'templates' / 'section.html')]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.tmp.cleanup()

    def test_card_sources_in_order_of_precedence(self):
        write(self.site, 'a/card.json', json.dumps({'title': 'From JSON', 'order': 3}))
        write(self.site, 'a/index.html', '<!-- bl-card\ntitle: Ignored\n-->')
        write(self.site, 'b/index.html', '<html><head><!-- bl-card\ntitle: From comment\nemoji: 🎲\norder: 1\ncta: Play →\n-->')
        write(self.site, 'c/index.md', '---\nlayout: post\ntitle: "From front matter"\ndescription: A guide.\n---\nText')
        write(self.site, 'd/index.html', '<title>From &amp; title</title><meta name="description" content="Meta text">')
        write(self.site, 'e/index.html', '<!-- bl-game-meta\ntitle: Old comment\n-->')
        cards = {c['title']: c for c in sections.cards_for(self.site)}
        self.assertEqual(set(cards), {'From JSON', 'From comment', 'From front matter', 'From & title', 'Old comment'})
        self.assertEqual(cards['From comment']['emoji'], '🎲')
        self.assertEqual(cards['From comment']['cta'], 'Play →')
        self.assertEqual(cards['From front matter']['description'], 'A guide.')
        self.assertEqual(cards['From & title']['description'], 'Meta text')
        self.assertEqual(cards['Old comment']['cta'], 'Open →')
        self.assertEqual(cards['From JSON']['path'], '/projects/a/')
        self.assertEqual([c['title'] for c in sections.cards_for(self.site)][:2], ['From comment', 'From JSON'])

    def test_unlisted_cards_and_outside_links(self):
        write(self.site, 'hidden/card.json', json.dumps({'title': 'Hidden', 'listed': 'no'}))
        write(self.site, 'hidden/index.html', '<html></html>')
        write(self.site, 'app/card.json', json.dumps({'title': 'App', 'link': 'https://example.invalid/app'}))
        cards = sections.cards_for(self.site)
        self.assertEqual([c['title'] for c in cards], ['App'])
        self.assertEqual(cards[0]['path'], 'https://example.invalid/app')

    def test_unknown_card_fields_and_bad_orders_are_errors(self):
        write(self.site, 'a/card.json', json.dumps({'title': 'A', 'colour': 'red'}))
        with self.assertRaises(ValueError):
            sections.cards_for(self.site)
        write(self.site, 'a/card.json', json.dumps({'title': 'A', 'order': 'first'}))
        with self.assertRaises(ValueError):
            sections.cards_for(self.site)

    def test_a_section_without_its_own_page_uses_the_template(self):
        write(self.site, 'plans/section.json', json.dumps({'title': 'Plans & <More>', 'intro': 'Each one page.'}))
        write(self.site, 'plans/one/index.html', '<!-- bl-card\ntitle: One\n-->')
        page = sections.render_section(self.site / 'plans')
        self.assertIn('<title>Plans &amp; &lt;More&gt;</title>', page)
        self.assertIn('<p>Each one page.</p>', page)
        self.assertIn('"title":"One"', page)
        self.assertNotIn(sections.PLACEHOLDER, page)
        self.assertEqual(sections.cards_for(self.site)[0]['title'], 'Plans & <More>')

    def test_a_template_page_is_described_by_its_section_description_or_else_its_intro(self):
        write(self.site, 'a/section.json', json.dumps({'title': 'A', 'description': 'Plans "to" keep & more', 'intro': 'Intro.'}))
        write(self.site, 'b/section.json', json.dumps({'title': 'B', 'intro': 'Only an intro.'}))
        self.assertEqual(Page(sections.render_section(self.site / 'a')).description, 'Plans "to" keep & more')
        self.assertEqual(Page(sections.render_section(self.site / 'b')).description, 'Only an intro.')

    def test_section_pages_list_their_cards_as_links_for_visitors_without_javascript(self):
        write(self.site, 'plans/section.json', json.dumps({'title': 'Plans'}))
        write(self.site, 'plans/one/index.html', '<!-- bl-card\ntitle: One & "Two"\ndescription: First <plan>\n-->')
        write(self.site, 'plans/away/card.json', json.dumps({'title': 'Away', 'link': 'https://example.invalid/x?a=1&b=2'}))
        write(self.site, 'plans/gone/card.json', json.dumps({'title': 'Gone', 'listed': 'no'}))
        page = sections.render_section(self.site / 'plans')
        found = Links(page)
        # Every link is inside <noscript>: with JavaScript, the page shows only the script's cards.
        self.assertEqual(found.links, [['https://example.invalid/x?a=1&b=2', 'Away', True],
                                       ['/projects/plans/one/', 'One & "Two"', True]])
        self.assertIn('First <plan>', found.noscript_text)
        self.assertNotIn('Gone', page)
        self.assertIn('"title":"Away"', page)  # the script's cards are unchanged
        self.assertNotIn(sections.NOSCRIPT_PLACEHOLDER, page)

    def test_a_section_page_needs_the_placeholder(self):
        write(self.site, 'index.html', '<script>const PROJECTS = [];</script>')
        with self.assertRaises(ValueError):
            sections.render_section(self.site)
        write(self.site, 'index.html', '<script>const PROJECTS = ' + sections.PLACEHOLDER + ';</script>')
        with self.assertRaises(ValueError):  # the links placeholder is missing
            sections.render_section(self.site)

    def test_card_text_that_looks_like_a_placeholder_stays_as_it_is(self):
        write(self.site, 'plans/section.json', json.dumps({'title': 'Plans'}))
        placeholders = [sections.PLACEHOLDER, sections.NOSCRIPT_PLACEHOLDER]
        for name, text in zip('ab', placeholders):
            write(self.site, f'plans/{name}/card.json', json.dumps({'title': name, 'description': text}))
        page = sections.render_section(self.site / 'plans')
        script = Links(page).script_text
        cards = json.loads(script[script.index('=') + 1:].strip().rstrip(';'))
        self.assertEqual([card['description'] for card in cards], placeholders)
        self.assertIn(sections.NOSCRIPT_PLACEHOLDER, Links(page).noscript_text)

    def test_which_pages_get_the_site_header(self):
        write(self.site, 'games/section.json', json.dumps({'title': 'Games'}))
        write(self.site, 'games/index.html', '<html><head></head><body></body></html>')
        write(self.site, 'games/pong/index.html', '<html><head></head><body></body></html>')
        write(self.site, 'plans/section.json', json.dumps({'title': 'Plans'}))
        write(self.site, 'plans/mine/index.html', '<html><head></head><body></body></html>')
        write(self.site, 'tool/index.html', '<html><head></head><body></body></html>')
        write(self.site, 'bare/card.json', json.dumps({'title': 'Bare', 'header': 'no'}))
        write(self.site, 'bare/index.html', '<html><head></head><body></body></html>')
        write(self.site, 'layout/index.html', '---\nlayout: project\n---\n<p>x</p>')
        write(self.site, 'guide/index.md', '---\ntitle: Guide\n---\nText')
        self.assertEqual(sections.wrapped_pages(self.site / 'games'),
                         ['games/index.html', 'plans/index.html', 'plans/mine/index.html', 'tool/index.html'])


if __name__ == '__main__':
    unittest.main()
