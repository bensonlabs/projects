"""Reading game pages with an HTML parser rather than text search (core rule 8).

A page only "has the site header" when it contains the header's elements or files: an element
whose id or class starts with bl-nav (or the old nav-autohide), or a link to the blog's
/assets/css/header.css or /assets/js/header.js. A comment or a string that merely mentions
bl-nav doesn't count.

A page's description is the content of its <meta name="description"> (found inside a Jekyll
page's head: block too, since that block becomes the page's <head>); a <meta http-equiv="refresh">
makes the page a redirect.
"""
from html.parser import HTMLParser

HEADER_ASSETS = ("/assets/css/header.css", "/assets/js/header.js")


def _is_header_name(name: str) -> bool:
    return name.startswith("bl-nav") or name == "nav-autohide"


class Page(HTMLParser):
    """Element ids, linked scripts and stylesheets, any trace of the blog's site header, the
    page's description and whether it redirects."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.ids: dict[str, int] = {}
        self.assets: list[str] = []
        self.site_header: list[str] = []
        self.tags: set[str] = set()
        self.description = ""
        self.redirect = False
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)
        attrs = {name: value or "" for name, value in attrs}
        element_id = attrs.get("id", "")
        if element_id:
            self.ids[element_id] = self.ids.get(element_id, 0) + 1
        for name in [element_id, *attrs.get("class", "").split()]:
            if name and _is_header_name(name):
                self.site_header.append(f'<{tag}> "{name}"')
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "")
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "refresh":
            self.redirect = True
        source = None
        if tag == "script" and attrs.get("src"):
            source = attrs["src"]
            self.assets.append(source)
        elif tag == "link" and attrs.get("href"):
            source = attrs["href"]
            if attrs.get("rel") == "stylesheet":
                self.assets.append(source)
        if source and (source in HEADER_ASSETS or "nav-autohide" in source):
            self.site_header.append(f"<{tag}> {source}")
