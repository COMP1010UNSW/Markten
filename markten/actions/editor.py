"""
# MarkTen / Actions / editor.py

Actions associated with text editors
"""
from logging import Logger
from pathlib import Path
from .process import run


log = Logger(__name__)


def vs_code(path: Path | None = None):
    """
    Launch VS Code at the given Path
    """
    # TODO: Add a hook to remove the temporary directory from VS Code's history
    return run("code", "-nw", *([str(path)] if path else []))
