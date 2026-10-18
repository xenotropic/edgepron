"""Discovery tests (vital-article parsing and dedupe)."""

from lexphon.discovery.intersection import dedupe, normalize_title
from lexphon.discovery.vital import _is_mainspace, fetch_vital_titles


class _FakeResponse:
    status_code = 200

    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


class _FakeSession:
    def __init__(self, pages):
        self._pages = pages

    def get(self, url, params=None, timeout=None):
        title = params["titles"].split("|")[0]
        content = self._pages.get(title)
        if content is None:
            return _FakeResponse({"query": {"pages": [{"title": title, "missing": True}]}})
        return _FakeResponse({"query": {"pages": [{
            "title": title,
            "revisions": [{"slots": {"main": {"content": content}}}],
        }]}})


def test_is_mainspace_rejects_namespaces():
    assert _is_mainspace("Earth")
    assert not _is_mainspace("Wikipedia:Vital articles/Level/1")
    assert not _is_mainspace("Wikipedia talk:Vital articles/Level/1")
    assert not _is_mainspace("Category:People")
    assert _is_mainspace("2001: A Space Odyssey")


def test_fetch_vital_titles_parses_articles_and_skips_chrome():
    pages = {
        "Wikipedia:Vital articles/Level 1": (
            "* [[Earth]]\n"
            "* [[Wikipedia talk:Vital articles/Level/1|Level 1 talk page]]\n"
            "{{Wikipedia:Vital articles/Level/header}}\n"
            "* [[Science]]\n"
            "[[Wikipedia:Vital articles/Level/2|Level 2]]\n"
        ),
    }
    titles = fetch_vital_titles(1, "http://example.invalid", _FakeSession(pages))
    assert titles == ["Earth", "Science"]


def test_fetch_vital_titles_follows_sublist_transclusions():
    pages = {
        "Wikipedia:Vital articles/Level 4": "{{Wikipedia:Vital articles/Level/4/People}}",
        "Wikipedia:Vital articles/Level/4/People": "* [[Aristotle]]\n* [[Socrates]]\n",
    }
    titles = fetch_vital_titles(4, "http://example.invalid", _FakeSession(pages))
    assert titles == ["Aristotle", "Socrates"]


def test_dedupe_preserves_first_seen_order():
    assert dedupe(["A", "B"], ["B", "C"], ["A"]) == ["A", "B", "C"]


def test_normalize_title():
    assert normalize_title("  Foo_Bar ") == "Foo Bar"
    assert normalize_title("") == ""