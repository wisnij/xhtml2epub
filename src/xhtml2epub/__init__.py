"""A library for converting ebooks in XHTML format into EPUB.

When writing or editing ebooks, it is often convenient to store them as a single
XHTML file which can be viewed with a web browser and edited using a normal text
editor, and then converted to EPUB later for reading on other devices such as a
phone or ebook reader.  This library provides a simple way to do this
conversion.

``xhtml2epub`` requires the XHTML source to follow two conventions to be
processed properly.  First, some basic information about the book should be
defined in the form of XML internal entity declarations in the document's DTD.
Currently, ``xhtml2epub`` recognizes the following entities as book metadata:

- ``title``
- ``author`` (or authors, but as a single string either way)
- ``language`` (such as "en")
- ``uid`` (a unique identifier, such as a UUID or ISBN)

All of these are optional, but recommended, especially if you want the resulting
EPUB file to conform to the EPUB standard.  (Why would you want a book without a
title, anyway?)

Secondly, in the XHTML file, any ``<div>`` element with an ``id`` attribute set
is assumed to be a separate chapter.  If the ``<div>`` has a ``title`` attribute
set, that is used as the title as shown in the book's table of contents.
Otherwise, the title will be auto-detected from the contents of any ``h1``,
``h2``, or ``h3`` heading elements immediately after the opening ``<div>``; or
if there are no such headings, from the ``id`` itself.

Chapter ``<div>`` elements may be nested to create sub-chapters, typically shown
in ebook readers as hierarchical trees.  For example, a book with a body
structure like this::

    <div id="chapter-1"><!-- content --></div>
    <div id="part-1">
      <!-- content -->
      <div id="chapter-2"><!-- content --></div>
      <div id="chapter-3"><!-- content --></div>
    </div>
    <div id="chapter-4"><!-- content --></div>

will show up in the table of contents as something like::

    - Chapter 1
    - Part 1
      - Chapter 2
      - Chapter 3
    - Chapter 4
"""

__all__ = ["Book"]
__author__ = "Jim Wisniewski <wisnij@gmail.com>"
__version__ = "1.1.1"

from xhtml2epub.book import Book
