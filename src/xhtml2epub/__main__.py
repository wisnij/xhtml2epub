"""Convert an XHTML ebook into EPUB format."""

import argparse
import os
import shutil
import sys
from typing import List, Optional

import pkg_resources

import xhtml2epub

_COPYRIGHT = f"""\
Copyright (c) 2021, 2022, 2023 {xhtml2epub.__author__}
License GPLv3+: GNU GPL version 3 or later <https://www.gnu.org/licenses/>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
"""


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        prog="xhtml2epub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-V",
        "--version",
        help="show version information and exit",
        action="version",
        version=f"%(prog)s {xhtml2epub.__version__} ({' '.join(xhtml2epub.__path__)})\n\n"
        + _COPYRIGHT,
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

    opts = parser.parse_args(args)
    if not (opts.write_template_dir or opts.input_xhtml):
        parser.print_help(sys.stderr)
        sys.exit(1)

    return opts


def main(args: Optional[List[str]] = None) -> Optional[int]:
    opts = parse_args(args)

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
    book = xhtml2epub.Book.parse(input_file)

    dest = output_file or book.epub_filename()
    if os.path.exists(dest):
        answer = input(f"overwrite {dest!r}? [y/N]: ")
        if not answer.lower().startswith("y"):
            return

    print(f"writing {dest!r}")
    book.write(dest)


if __name__ == "__main__":
    sys.exit(main())
