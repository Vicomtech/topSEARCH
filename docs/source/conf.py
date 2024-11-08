# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'topFIND'
copyright = '2023, Ander Cejudo, Garazi Artola, Teresa García, Amaia Calvo, Yone Tellechea'
author = 'Ander Cejudo, Garazi Artola, Teresa García, Amaia Calvo, Yone Tellechea'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon', "myst_parser"]
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
#html_static_path = ['_static']

# https://sphinx-themes.org/sample-sites/sphinx-rtd-theme/
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'navigation_depth': 4,
}
