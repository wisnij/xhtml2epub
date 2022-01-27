"""Convert an XHTML ebook into EPUB format."""

import argparse
import os
import pkg_resources
import shutil
import sys
from typing import List, Optional

from xhtml2epub import Book


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, prog="xhtml2epub")
    parser.add_argument(
        "-V",
        "--version",
        help="show version information and exit",
        action="store_true",
    )
    parser.add_argument(
        "-i", "--input-xhtml", metavar="INPUT.XHTML", help="path to the input file"
    )
    parser.add_argument(
        "-o",
        "--output-epub",
        metavar="OUTPUT.EPUB",
        help='write epub output to OUTPUT.EPUB (defaults to "Author - Title.epub")',
    )
    parser.add_argument(
        "-t",
        "--write-template-dir",
        metavar="OUTPUT_DIR",
        help="write ebook template files to OUTPUT_DIR",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> Optional[int]:
    opts = parse_args(args)

    if opts.version:
        import xhtml2epub.version

        print(f"xhtml2epub {xhtml2epub.version.__version__}")
        return

    if opts.write_template_dir:
        _write_template_dir(opts.write_template_dir)

    if opts.input_xhtml:
        _convert_ebook(opts.input_xhtml, opts.output_epub)


def _write_template_dir(destination_dir: str) -> None:
    source_dir = pkg_resources.resource_filename(__name__, "template")
    print(f"copying template files to {destination_dir!r}")

    def copy(src, dest):
        print(f">>> {dest!r}")
        shutil.copy2(src, dest)

    shutil.copytree(source_dir, destination_dir, copy_function=copy)


def _convert_ebook(input_file: str, output_file: Optional[str] = None) -> None:
    print(f"reading {input_file!r}")
    book = Book.parse(input_file)

    dest = output_file or book.epub_filename()
    if os.path.exists(dest):
        answer = input(f"overwrite {dest!r}? [y/N]: ")
        if not answer.lower().startswith("y"):
            return

    print(f"writing {dest!r}")
    book.write(dest)


if __name__ == "__main__":
    sys.exit(main())
