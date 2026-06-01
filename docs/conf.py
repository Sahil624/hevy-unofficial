"""Sphinx configuration for hevy-unofficial."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
REPO_ROOT = DOCS_DIR.parent
PACKAGE_SRC = REPO_ROOT / "packages" / "hevy" / "src"

sys.path.insert(0, str(PACKAGE_SRC))

project = "hevy-unofficial"
author = "hevy-unofficial contributors"
copyright = f"{datetime.now().year}, {author}"
release = "0.1.0"
version = release

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

autosummary_generate = True
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "show-inheritance": True,
}
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = "hevy-unofficial"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# GitHub Pages project site: https://<owner>.github.io/<repo>/
_docs_base = os.environ.get("DOCS_BASE_URL", "").rstrip("/")
if _docs_base:
    html_baseurl = f"{_docs_base}/"

html_theme_options = {
    "source_repository": "https://github.com/Sahil624/hevy-unofficial",
    "source_branch": "main",
    "source_directory": "docs/",
    "light_logo": None,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/Sahil624/hevy-unofficial",
            "html": "",
            "class": "fa-brands fa-github",
        },
    ],
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", "https://pydantic.dev/docs/validation/latest/objects.inv"),
}

# Re-exported symbols in hevy_unofficial.__init__ duplicate autodoc targets.
suppress_warnings = ["ref.python"]

pygments_style = "sphinx"
