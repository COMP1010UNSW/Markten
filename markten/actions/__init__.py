"""
# MarkTen / actions

Code defining actions that are run during the marking recipe.
"""
from . import editor, git, process, python, time, webbrowser
from .__action import MarkTenAction

__all__ = [
    'MarkTenAction',
    'editor',
    'git',
    'process',
    'python',
    'time',
    'webbrowser',
]
