"""SEO checks on the built site. Standard library only.

Run with scripts/check-site.sh, which builds a production copy of the site
(drafts off) into a temp folder and points SITE_DIR at it.
"""
import json
import os
import re
import subprocess
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

REPO = Path(__file__).resolve().parent.parent
SITE = Path(os.environ.get("SITE_DIR", REPO / "public"))
HOST = "montepy.in"
BASE = f"https://{HOST}/"

# Accepted exceptions. Each one has a reason; keep this list short.
SHORT_TITLE_OK = {
    "/": "the home title is the brand name only (theme behaviour)",
}
PAGINATED = re.compile(r"(^|/)page/\d+/$")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles, self.descriptions, self.canonicals = [], [], []
        self.robots, self.refs, self.jsonld, self.h1 = "", [], [], 0
        self.social = []
        self._in_title = self._in_ld = self._in_social = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title, self._buf = True, ""
        elif tag == "meta" and a.get("name") == "description":
            self.descriptions.append(a.get("content", ""))
        elif tag == "meta" and a.get("name") == "robots":
            self.robots = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, ""
        elif tag == "h1":
            self.h1 += 1
        elif tag == "div" and "social-icons" in (a.get("class") or ""):
            self._in_social = True
        if tag == "a" and a.get("href"):
            self.refs.append(a["href"])
            if self._in_social:
                self.social.append(a["href"])
        if tag in ("img", "script") and a.get("src"):
            self.refs.append(a["src"])
        if tag == "link" and a.get("rel") != "canonical" and a.get("href"):
            self.refs.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.titles.append(self._buf.strip())
        elif tag == "script" and self._in_ld:
            self._in_ld = False
            self.jsonld.append(self._buf)
        elif tag == "div":
            self._in_social = False

    def handle_data(self, data):
        if self._in_title or self._in_ld:
            self._buf += data


def load_pages():
    pages = {}
    for f in SITE.rglob("*.html"):
        html = f.read_text(encoding="utf-8")
        if re.search(r'http-equiv="?refresh', html):
            continue  # Hugo alias redirect stub
        rel = f.relative_to(SITE).as_posix()
        if rel == "404.html":
            continue
        path = "/" + re.sub(r"(^|/)index\.html$", r"\1", rel)
        p = Page()
        p.feed(html)
        pages[path] = p
    return pages


def resolve(url):
    """True if the URL is a file in the build, 'slash' if it only works with
    a trailing slash added (a 301 on GitHub Pages), else False."""
    path = unquote(urlparse(url).path).lstrip("/")
    target = SITE / path
    if path == "" or path.endswith("/"):
        return (target / "index.html").is_file()
    if target.is_file():
        return True
    return "slash" if (target / "index.html").is_file() else False


def indexable(path, page):
    return "noindex" not in page.robots and not PAGINATED.search(path)


@unittest.skipUnless((SITE / "index.html").is_file(), f"no build in {SITE}")
class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = load_pages()

    def test_titles_30_to_60_chars(self):
        for path, p in self.pages.items():
            if not indexable(path, p) or path in SHORT_TITLE_OK:
                continue
            with self.subTest(path=path):
                self.assertEqual(len(p.titles), 1)
                self.assertTrue(30 <= len(p.titles[0]) <= 60, p.titles[0])

    def test_descriptions_110_to_160_chars_and_unique(self):
        seen = {}
        for path, p in self.pages.items():
            if not indexable(path, p):
                continue
            with self.subTest(path=path):
                self.assertEqual(len(p.descriptions), 1)
                d = p.descriptions[0].strip()
                self.assertTrue(110 <= len(d) <= 160, f"{len(d)}: {d}")
                self.assertNotIn(d, seen, f"same description as {seen.get(d)}")
                seen[d] = path

    def test_one_canonical_that_resolves(self):
        for path, p in self.pages.items():
            with self.subTest(path=path):
                self.assertEqual(len(p.canonicals), 1)
                c = p.canonicals[0]
                if urlparse(c).netloc != HOST:
                    continue  # cross-domain canonical: syndicated post
                if PAGINATED.search(path):
                    self.assertEqual(c, BASE + PAGINATED.sub(r"\1", path).lstrip("/"))
                else:
                    self.assertEqual(c, BASE + path.lstrip("/"))

    def test_internal_refs_resolve_without_redirect(self):
        for path, p in self.pages.items():
            for ref in p.refs:
                url = urljoin(BASE + path.lstrip("/"), ref)
                if urlparse(url).netloc != HOST:
                    continue
                with self.subTest(page=path, ref=ref):
                    self.assertIs(resolve(url.split("#")[0]), True)

    def test_one_h1_per_page(self):
        for path, p in self.pages.items():
            if PAGINATED.search(path):
                continue  # theme renders page 2+ of a list without a header
            with self.subTest(path=path):
                self.assertEqual(p.h1, 1)

    def test_jsonld_is_valid_json(self):
        for path, p in self.pages.items():
            for block in p.jsonld:
                with self.subTest(path=path):
                    json.loads(block)

    def test_organization_jsonld_is_complete(self):
        home = self.pages["/"]
        orgs = [d for d in map(json.loads, home.jsonld) if d.get("@type") == "Organization"]
        self.assertEqual(len(orgs), 1)
        org = orgs[0]
        for key in ("name", "url", "logo", "sameAs"):
            self.assertTrue(org.get(key), key)
        self.assertTrue(org["logo"].endswith(".png"), org["logo"])
        self.assertIs(resolve(org["logo"]), True)
        # sameAs is the same list as the social icons, without mailto: links.
        profiles = [u for u in home.social if u.startswith("https://")]
        self.assertTrue(profiles)
        self.assertEqual(org["sameAs"], profiles)

    def test_blogposting_logo_resolves(self):
        for path, p in self.pages.items():
            for d in map(json.loads, p.jsonld):
                if d.get("@type") == "BlogPosting":
                    with self.subTest(path=path):
                        self.assertIs(resolve(d["publisher"]["logo"]["url"]), True)

    def test_no_draft_posts_in_build(self):
        for d in (SITE / "posts").iterdir():
            if not (d / "index.html").is_file() or d.name == "page":
                continue
            src = REPO / "content" / "posts" / f"{d.name}.md"
            with self.subTest(post=d.name):
                self.assertTrue(src.is_file(), "built page has no source file")
                self.assertNotRegex(src.read_text(encoding="utf-8"), r"(?m)^draft:\s*true")

    def test_sitemap_lists_only_indexable_built_pages(self):
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap):
            with self.subTest(loc=loc):
                self.assertIs(resolve(loc), True)
                page = self.pages.get("/" + urlparse(loc).path.lstrip("/"))
                if page is not None:
                    self.assertNotIn("noindex", page.robots)
        self.assertNotIn(BASE + "search/", sitemap)

    def test_term_pages_with_index_file_list_posts(self):
        # A term _index.md without published posts builds an empty page.
        for taxonomy in ("tags", "categories"):
            for index in (REPO / "content" / taxonomy).glob("*/_index.md"):
                built = SITE / taxonomy / index.parent.name / "index.html"
                with self.subTest(term=f"{taxonomy}/{index.parent.name}"):
                    self.assertTrue(built.is_file())
                    self.assertIn("post-entry", built.read_text(encoding="utf-8"))

    def test_llms_txt(self):
        text = (SITE / "llms.txt").read_text(encoding="utf-8")
        home = self.pages["/"]
        lines = text.splitlines()
        self.assertEqual(lines[0], "# Monte's Snippets")
        # The summary is the same text as the home meta description.
        self.assertIn(f"> {home.descriptions[0]}", lines)
        # Every published post is listed once, with a summary; nothing else.
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        posts = set(re.findall(r"<loc>(https://montepy\.in/posts/[^/<]+/)</loc>", sitemap))
        listed = re.findall(r"^- \[[^\]]+\]\((https://montepy\.in/posts/[^)]+)\): \S", text, re.M)
        self.assertEqual(sorted(listed), sorted(posts))
        # Contact holds the X and LinkedIn profiles from the social icons.
        contact = text.split("## Contact", 1)[1]
        wanted = [u for u in home.social if "x.com/" in u or "linkedin.com/" in u]
        self.assertEqual(len(wanted), 2)
        self.assertEqual(re.findall(r"\]\((https://[^)]+)\)", contact), wanted)

    def test_search_page_is_noindex(self):
        self.assertIn("noindex", self.pages["/search/"].robots)


class RepoTest(unittest.TestCase):
    def test_header_logo_matches_icon_shape(self):
        sys.path.insert(0, str(REPO / "scripts"))
        from make_icons import M

        config = (REPO / "config.yml").read_text(encoding="utf-8")
        points = re.search(r'iconSVG:.*?<polygon points="([^"]+)"', config).group(1)
        self.assertEqual(points, " ".join(f"{x},{y}" for x, y in M))

    def test_build_output_is_not_tracked(self):
        out = subprocess.run(["git", "ls-files", "public"], cwd=REPO,
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "", "public/ is build output; CI builds it")


if __name__ == "__main__":
    unittest.main()
