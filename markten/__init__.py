"""
# MarkTen

A manual marking automation framework.
"""
from . import actions, parameters
from .__action_session import ActionSession
from .__consts import VERSION as __version__
from .__recipe import Recipe
from .actions import MarktenAction

__all__ = [
    'ActionSession',
    'MarktenAction',
    'Recipe',
    'parameters',
    'actions',
    '__version__',
]
