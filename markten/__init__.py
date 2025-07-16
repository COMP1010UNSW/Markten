"""
# MarkTen

A manual marking automation framework.
"""
# Intentionally disable import sorting so that we don't get circular import
# annoyance for importing common types such as `ActionSession`
from .__action_session import ActionSession  # noqa: I001
from .__consts import VERSION as __version__
from .__recipe import Recipe
from .actions import MarktenAction

from . import actions, parameters

__all__ = [
    'ActionSession',
    'MarktenAction',
    'Recipe',
    'parameters',
    'actions',
    '__version__',
]
