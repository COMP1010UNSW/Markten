"""
# Markten / actions

Code defining actions that are run during the marking recipe.
"""

from . import editor, git, process, time, webbrowser
from .__action import MarktenAction
from .__misc import open

__all__ = [
    "MarktenAction",
    "editor",
    "git",
    "open",
    "process",
    "time",
    "webbrowser",
]
