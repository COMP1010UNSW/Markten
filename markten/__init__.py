"""
# MarkTen

A manual marking automation framework.
"""
from . import actions, parameters
from .__consts import VERSION as __version__
from .__recipe import Recipe

__all__ = [
    'Recipe',
    'parameters',
    'actions',
    '__version__',
]
