"""
Sphinx configuration for Simple Nebula API documentation.
"""
import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'Simple Nebula API'
copyright = f'{datetime.now().year}, Your Name'
author = 'Your Name'
release = '1.0.0'

# The full version, including alpha/beta/rc tags
version = '1.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The theme to use for HTML and HTML Help pages
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Extension settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/5.2/', None),
    'djangorestframework': ('https://www.django-rest-framework.org/', None),
} 