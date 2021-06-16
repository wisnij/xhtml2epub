from dataclasses import dataclass
from ebooklib import epub
import json
from lxml import etree
from lxml.etree import Element, _ElementTree as ElementTree
from lxml.html import HtmlEntity, XHTMLParser
import os.path
import re
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

import xhtml2epub.html


@dataclass
class ChapterContent:
    """The contents of a single chapter."""

    id: str
    title: str
    element: Element


@dataclass
class ChapterTree:
    """The contents of a chapter and any subchapters nested under it."""

    children: List["ChapterTree"]
    content: Optional[ChapterContent] = None


class Book:
    """An ebook that can be serialized as EPUB."""

    def __init__(
        self,
        content: ElementTree,
        source: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        language: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> None:
        """:param content: the book's contents as an ``lxml.ElementTree`` object
        :param source: path to the file where the source was read from, if any.
            If omitted, any relative paths to files within the book
            (e.g. images) will be interpreted relative to the current directory
            rather than from the source file's location.
        :param title: title of the book
        :param author: author(s) of the book
        :param language: language the book is written in
        :param uid: a unique identifier for the EPUB book
        """
        self.source = source
        if source:
            self.source_dir = os.path.dirname(source)
        self.title = title
        self.author = author
        self.language = language
        self.uid = uid
        self._parse_content(content)

    @classmethod
    def parse(cls, source: str) -> "Book":
        """Create a new ``Book`` object from the XHTML ``source`` file.

        :param source: path to the XHTML file to parse
        """
        parser = XHTMLParser(remove_blank_text=True, resolve_entities=False)
        tree = etree.parse(source, parser)

        # Strip the standard XHTML namespace from tags, but leave any others in place
        for elt in tree.iter(tag=Element):
            elt.tag = elt.tag.replace("{http://www.w3.org/1999/xhtml}", "")

        entities = cls._internal_entities(tree)
        return Book(
            content=tree,
            source=source,
            title=entities.get("title"),
            author=entities.get("author"),
            language=entities.get("language", "en"),
            uid=entities.get("uid"),
        )

    @classmethod
    def _internal_entities(cls, tree: ElementTree) -> Dict[str, str]:
        """Return a dict of entities defined in the ``tree``'s internal DTD."""
        return {e.name: e.content for e in tree.docinfo.internalDTD.entities()}

    def _parse_content(self, content: ElementTree) -> None:
        """Walk the XML DOM and detect book structure."""
        self.content = content
        self.entities = xhtml2epub.html.entities.copy()
        self.entities.update(self._internal_entities(content))

        self.images, self.cover = self._find_images(content)
        self.stylesheets = self._find_stylesheets(content)

        chapters = self._find_chapters(content.find("body"))
        self.chapters = chapters.children
        if not self.chapters:
            print(f"WARNING: no chapters found in {self.source or self.content!r}", file=sys.stderr)

    def _find_images(self, content: ElementTree) -> Tuple[Dict[str, str], str]:
        """Find all images in the book and store their ``src``."""
        images = {}
        cover = None

        for img in content.iterfind(".//img"):
            source = img.attrib["src"]
            basename = self._basename(source)
            img_id = f"img.{basename}"

            if img_id not in images:
                images[img_id] = source
                if "alt" not in img.attrib:
                    img.attrib["alt"] = basename.capitalize()
                if not cover:
                    cover = img_id

        return (images, cover)

    def _basename(self, path: str) -> str:
        """Return a file ``path``'s basename with file extension removed."""
        return os.path.splitext(os.path.basename(path))[0]

    def _find_stylesheets(self, content: ElementTree) -> List[Dict[str, str]]:
        """Find all linked stylesheets in the book."""
        links = content.xpath('//link[@rel="stylesheet"]')
        return [dict(link.attrib) for link in links]

    def _find_chapters(self, element: Element) -> ChapterTree:
        """Find all chapters under ``element``.

        A chapter is a ``div`` with the ``id`` attribute set.
        """
        child_divs = element.xpath("div[@id]")
        for child in child_divs:
            element.remove(child)

        chapter = ChapterTree(children=[self._find_chapters(div) for div in child_divs])
        if element.tag == "div":
            chapter.content = self._extract_chapter(element)

        return chapter

    def _extract_chapter(self, element: Element) -> ChapterContent:
        """Parse the chapter in ``element`` to determine its id and title."""
        chapter_id = element.attrib["id"]
        title = element.attrib.get("title")
        if not title:
            title_parts = []
            for child in element:
                if child.tag in {"h1", "h2", "h3"}:
                    title_parts.append(self._text(child))
                else:
                    break

            if title_parts:
                title = ": ".join(title_parts)
            else:
                title = re.sub("[-_]", " ", chapter_id).title()

        return ChapterContent(chapter_id, title, element)

    def _text(self, element: Element) -> str:
        """Extract the text content of ``element`` and its children, expanding entity
        references as needed.
        """
        if isinstance(element, HtmlEntity):
            return self.entities[element.name] + (element.tail or "")
        else:
            child_texts = [self._text(child) for child in element]
            return "".join([element.text or "", *child_texts, element.tail or ""])

    def write(self, dest: str) -> None:
        """Write the book's content to ``dest`` as EPUB."""
        book = epub.EpubBook()
        if self.title:
            book.set_title(self.title)
        if self.author:
            book.add_author(self.author)
        if self.language:
            book.set_language(self.language)
        if self.uid:
            book.set_identifier(self.uid)

        self._add_images(book)
        self._add_stylesheets(book)
        self._add_chapters(book)

        epub.write_epub(dest, book)

    def epub_filename(self) -> str:
        """Suggest a name for the EPUB file based on the book's author and title."""
        return (
            f"{self.author or 'Unknown Author'} - {self.title or 'Unknown Title'}.epub"
        )

    def _add_images(self, book: epub.EpubBook) -> None:
        """Add EPUB entries for each image in the book to ``book``."""
        for img_id, img_src in self.images.items():
            img_bytes = self._read_book_file(img_src)
            if img_id == self.cover:
                book.set_cover(img_src, img_bytes, create_page=False)
            else:
                img_item = epub.EpubItem(
                    uid=img_id, file_name=img_src, content=img_bytes
                )
                book.add_item(img_item)

    def _add_stylesheets(self, book: epub.EpubBook) -> None:
        """Add EPUB entries for all linked stylesheets to ``book``."""
        for sheet in self.stylesheets:
            filename = sheet["href"]
            sheet_id = self._basename(filename)
            sheet_bytes = self._read_book_file(filename)
            sheet_item = epub.EpubItem(
                uid=sheet_id,
                file_name=filename,
                media_type=sheet.get("type"),
                content=sheet_bytes,
            )
            book.add_item(sheet_item)

    def _read_book_file(self, path: str) -> bytes:
        """Open a file referenced in the book and return its content as bytes."""
        # TODO: support fetching from URL?
        if os.path.isabs(path) or not self.source_dir:
            abspath = path
        else:
            abspath = os.path.join(self.source_dir, path)

        with open(abspath, "rb") as stream:
            return stream.read()

    def _add_chapters(self, book: epub.EpubBook) -> None:
        """Add entries for all chapters to the ``book``'s TOC and spine."""
        toc = []
        self.spine = []
        for chapter in self.chapters:
            toc.append(self._add_chapter(book, chapter))

        book.toc = toc
        book.spine = self.spine

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

    def _add_chapter(
        self, book: epub.EpubBook, chapter: ChapterTree
    ) -> Union[epub.EpubItem, Tuple[epub.EpubItem, List[epub.EpubItem]]]:
        """Add a TOC entry for ``chapter`` and all of its children to ``book``."""
        content = chapter.content

        element = content.element
        if len(element):
            # This section has some text content other than its children, so
            # create a separate page for it and insert it into the book spine
            chapter_item = epub.EpubHtml(
                uid=content.id,
                title=content.title,
                file_name=f"{content.id}.xhtml",
                content=self._element_xhtml(content.element),
            )
            chapter_item.links = self.stylesheets
            book.add_item(chapter_item)
            self.spine.append(chapter_item)
        else:
            # Empty section just for grouping; no page, no spine entry
            chapter_item = epub.Section(content.title)

        children = chapter.children
        if children:
            child_items = [self._add_chapter(book, child) for child in children]
            return (chapter_item, child_items)
        else:
            return chapter_item

    def _element_xhtml(self, element: Element) -> bytes:
        """Return the contents of ``element`` as XHTML, omitting the top-level element tag itself."""
        raw_content = b"".join(etree.tostring(e) for e in element)

        def expand_entity(match) -> bytes:
            is_num, is_hex, code = match.groups()
            if is_num:
                return chr(int(code, base=16 if is_hex else 10)).encode()

            code = code.decode()
            if code in self.entities:
                return self.entities[code].encode()
            else:
                return match.group()

        encoded_content = re.sub(
            b"&(#(x)?)?([A-Za-z0-9]+);", expand_entity, raw_content
        )
        return encoded_content
