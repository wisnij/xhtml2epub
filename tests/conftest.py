import importlib.resources
from pathlib import Path
import shutil

import pytest


@pytest.fixture()
def template_copy(tmp_path: Path) -> Path:
    """Copy the bundled template directory into a temp directory and return it."""
    dest_dir = tmp_path / "template"
    with importlib.resources.path("xhtml2epub", "template") as src_dir:
        shutil.copytree(src_dir, dest_dir)
        return dest_dir


@pytest.fixture()
def book_source(template_copy: Path) -> Path:
    """Return the path to the copied template's index.xhtml to use as input."""
    return template_copy / "index.xhtml"
