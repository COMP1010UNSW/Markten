"""
# Markten / Actions / editor / interface

General interface for text editors.
"""

from collections.abc import Awaitable
from pathlib import Path
from typing import Protocol

from markten import ActionSession


class TextEditorAction(Protocol):
    """
    A generic interface for a text editor. Some text editors may offer more
    features than this protocol, but it is intended that all text editors
    conform to this protocol at least.

    Note that the pyright type-checker appears to misbehave when it comes to
    type-checking methods using.

    Parameters
    ----------
    action : ActionSession
        Action session
    paths : *Path
        Paths to open in text editor.
    """

    def __call__(
        self,
        action: ActionSession,
        *paths: Path,
    ) -> Awaitable[None]: ...
