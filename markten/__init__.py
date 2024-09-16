"""
# MarkTen

A manual marking automation framework.
"""
from .__markten import MarkTen
from . import generators
from . import actions


__all__ = [
    'MarkTen',
    'generators',
    'actions',
]
