"""
# MarkTen

A manual marking automation framework.
"""
from .__recipe import Recipe
from . import generators
from . import actions


__all__ = [
    'Recipe',
    'generators',
    'actions',
]
