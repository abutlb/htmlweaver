__version__ = "1.0.0"
__author__ = "abutlb"
__description__ = "Split HTML into threads. Weave them back together."

from .splitter import split_html
from .combiner import combine_html

__all__ = ['split_html', 'combine_html']
