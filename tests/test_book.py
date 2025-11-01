from pathlib import Path
from typing import Union

from ebooklib.epub import EpubItem

from xhtml2epub import Book


def toc_struct(item: Union[EpubItem, tuple, list]) -> Union[dict, list]:
    """Recursively extract the nested table of contents from a book and return
    it as a Python data structure.
    """
    if isinstance(item, list):
        return [toc_struct(i) for i in item]
    elif isinstance(item, tuple):
        section, children = item
        struct = toc_struct(section)
        struct["children"] = toc_struct(children)
        return struct
    else:
        return {
            "id": item.id if isinstance(item, EpubItem) else None,
            "title": item.title,
        }


class TestBook:
    def test_parse_template(self, book_source: Path) -> None:
        book = Book.parse(book_source)

        assert book.title == "TITLE"
        assert book.author == "AUTHOR"
        assert book.language == "LANGUAGE"
        assert book.uid == "IDENTIFIER"

        # Images and cover
        assert book.images  # at least one image found
        assert book.cover in book.images
        assert book.images[book.cover] == "cover.jpg"

        # Stylesheet
        assert any(s.get("href") == "stylesheet.css" for s in book.stylesheets)

        # Chapter detection from top-level divs
        top_ids = [c.content.id for c in book.chapters]
        assert top_ids[:3] == ["cover", "title-page", "chapter-1"]

    def test_epub_filename(self, book_source: Path) -> None:
        book = Book.parse(book_source)
        assert book.epub_filename() == "AUTHOR - TITLE.epub"

    def test_toc(self, book_source: Path) -> None:
        book = Book.parse(book_source)
        epub = book.to_epub()

        expected = [
            {"id": "cover", "title": "Cover"},
            {"id": "title-page", "title": "Title Page"},
            {"id": "chapter-1", "title": "Chapter 1: A chapter title"},
            {"id": "chapter-2", "title": "A title attribute"},
            {
                "id": "chapter-3",
                "title": "A nested chapter with content",
                "children": [
                    {"id": "section-3.1", "title": "Section 3.1"},
                    {"id": "section-3.2", "title": "Section 3.2"},
                ],
            },
            {
                "id": None,
                "title": "A nested chapter with no content",
                "children": [
                    {"id": "section-4.1", "title": "Section 4.1"},
                    {"id": "section-4.2", "title": "Section 4.2"},
                ],
            },
        ]

        assert toc_struct(epub.toc) == expected

    def test_metadata(self, book_source: Path) -> None:
        book = Book.parse(book_source)
        epub = book.to_epub()

        assert epub.get_metadata("DC", "title") == [("TITLE", None)]
        assert epub.get_metadata("DC", "creator") == [("AUTHOR", {"id": "creator"})]
        assert epub.get_metadata("DC", "language") == [("LANGUAGE", None)]
        assert epub.get_metadata("DC", "identifier") == [("IDENTIFIER", {"id": "id"})]

    def test_entities(self, book_source: Path) -> None:
        book = Book.parse(book_source)
        epub = book.to_epub()
        chapter1 = epub.get_item_with_id("chapter-1")
        content = chapter1.get_content().decode()

        # Named quotes expanded to unicode characters
        assert "&ldquo;" not in content
        assert "&rdquo;" not in content
        assert "\u201c" in content
        assert "\u201d" in content

        # Copyright numeric entities expanded
        assert "&#169;" not in content
        assert "&#xA9;" not in content
        assert "\xa9" in content

        # These entities should remain literal
        assert "&amp;" in content
        assert "&lt;" in content
        assert "&gt;" in content

        # ...and we didn't double-escape anything by mistake
        assert "&amp;amp;" not in content
