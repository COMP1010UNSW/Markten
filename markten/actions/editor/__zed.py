"""
# Markten / Actions / __editor

Actions associated with text editors
"""

from pathlib import Path
from typing import TYPE_CHECKING, cast

from markten.__action_session import ActionSession
from markten.actions import process
from markten.actions.__action import markten_action
from markten.actions.editor.__interface import TextEditorAction


@markten_action
async def zed(
    action: ActionSession,
    *paths: Path,
):
    """
    Launch a new Zed window with the given Paths.
    """
    # -n = new window
    # -w = CLI waits for window exit
    _ = await process.run(
        action.make_child(process.run),
        "zed",
        "-nw",
        *[str(p) for p in paths],
    )


if TYPE_CHECKING:
    validate_calling_behaviour: TextEditorAction = cast(TextEditorAction, zed)
    _ = validate_calling_behaviour(ActionSession(""), Path("foo"), Path("foo"))

    # Basedpyright is not happy with this, but mypy is. It seems correct from
    # my checking.
    validate_type_compatibility: TextEditorAction = zed
