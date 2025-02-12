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
    action = run("code", "-nw", *([str(path)] if path else []))

    # Add a hook to remove the temporary directory from VS Code's history
    async def remove_from_history():
        # TODO: Implement this using info from the StackOverflow answer
        # https://stackoverflow.com/a/74933036/6335363
        # Kinda painful that it's not just a JSON file tbh
        ...
    action.register_cleanup_hook(remove_from_history)
    return action
