# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../src' ))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'tonika-bus'
copyright = '2025, aa-parky'
author = 'aa-parky'
release = '0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Extensions
extensions = [
    'sphinx.ext.autodoc',      # Auto-generate from docstrings
    'sphinx.ext.napoleon',     # Support Google/NumPy docstring styles
    'sphinx.ext.viewcode',     # Add source code links
    'sphinx.ext.intersphinx',  # Link to other projects
    'sphinx.ext.autosummary',  # Generate summary tables
    'myst_parser',             # Markdown support via MyST
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Theme
html_theme = 'sphinx_rtd_theme'  # ReadTheDocs theme

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon settings (for Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
html_static_path = ['_static']

# Recognize both .rst and .md sources
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# MyST configuration: treat all Markdown links as external to avoid cross-ref warnings
myst_all_links_external = True
