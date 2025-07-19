"""
# Markten / actions

Code defining actions that are run during the marking recipe.
"""

from . import editor, email, git, process, time, webbrowser
from .__action import MarktenAction
from .__misc import open

__all__ = [
    "MarktenAction",
    "editor",
    "email",
    "git",
    "open",
    "process",
    "time",
    "webbrowser",
]
