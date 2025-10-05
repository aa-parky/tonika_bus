# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "tonika-bus"
copyright = "2025, aa-parky"
author = "aa-parky"
release = "0.2.0"

# Add build timestamp for peace of mind
build_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
html_last_updated_fmt = "%Y-%m-%d %H:%M:%S UTC"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Extensions
extensions = [
    "sphinx.ext.autodoc",  # Auto-generate from docstrings
    "sphinx.ext.napoleon",  # Support Google/NumPy docstring styles
    "sphinx.ext.viewcode",  # Add source code links
    "sphinx.ext.intersphinx",  # Link to other projects
    "sphinx.ext.autosummary",  # Generate summary tables
    "myst_parser",  # Markdown support via MyST
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Theme
html_theme = "sphinx_rtd_theme"  # ReadTheDocs theme

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# Napoleon settings (for Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
html_static_path = ["_static"]

# Recognize both .rst and .md sources
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# MyST configuration: treat all Markdown links as external to avoid cross-ref warnings
myst_all_links_external = True

# Add build date to HTML context for display in footer
html_context = {
    'build_date': build_date,
}

# Show "Last updated" in the footer
html_show_sphinx = True
