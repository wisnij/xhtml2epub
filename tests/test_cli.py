from pathlib import Path

import pytest

from xhtml2epub.__main__ import main, parse_args


class TestCLI:
    def test_parse_args_in(self) -> None:
        opts = parse_args(["-i", "in.xhtml"])
        assert opts.input_xhtml == "in.xhtml"
        assert opts.output_epub is None

    def test_parse_args_in_out(self) -> None:
        opts = parse_args(["-i", "in.xhtml", "-o", "out.epub"])
        assert opts.input_xhtml == "in.xhtml"
        assert opts.output_epub == "out.epub"

    def test_parse_args_out_only(self) -> None:
        """Should fail if neither -i nor -t are specified."""
        with pytest.raises(SystemExit):
            parse_args(["-o", "out.epub"])

    def test_parse_args_template(self) -> None:
        opts = parse_args(["-t", "dir-name"])
        assert opts.write_template_dir == "dir-name"

    def test_write_template_dir(self, tmp_path: Path) -> None:
        out_dir = tmp_path / "template_out"
        main(["-t", str(out_dir)])

        assert out_dir.exists()
        assert (out_dir / "index.xhtml").exists()
        assert (out_dir / "stylesheet.css").exists()
        assert (out_dir / "cover.jpg").exists()

    def test_convert_e2e(self, book_source: Path, tmp_path: Path) -> None:
        dest = tmp_path / "book.epub"
        assert not dest.exists()

        main(["-i", str(book_source), "-o", str(dest)])

        assert dest.exists()
        assert dest.stat().st_size > 0
