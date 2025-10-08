"""
# Markten / Actions / __editor

Actions associated with text editors
"""

import json
import logging
from pathlib import Path
from shutil import copyfile
from typing import NotRequired, TypedDict

import aiosqlite
import platformdirs

from markten.__action_session import ActionSession
from markten.actions import process
from markten.actions.__action import markten_action

log = logging.getLogger(__name__)


class VsCodeHistoryEntry(TypedDict):
    folderUri: NotRequired[str]
    """
    Path to folder, in the form `file://{path}`
    """
    fileUri: NotRequired[str]
    """Path to file, in the form `file://{path}`"""
    label: NotRequired[str]
    remoteAuthority: NotRequired[str]


@markten_action
async def vs_code(
    action: ActionSession,
    path: Path | None = None,
    remove_history: bool = False,
):
    """
    Launch a new VS Code window at the given Path.
    """
    # -n = new window
    # -w = CLI waits for window exit
    _ = await process.run(
        action.make_child(process.run),
        "code",
        "-nw",
        *([str(path)] if path else []),
    )

    # Add a hook to remove the temporary directory from VS Code's history
    async def cleanup_vscode_history():
        """
        Access VS Code's state database, in order to remove recent items from
        the data.

        Adapted from https://stackoverflow.com/a/74933036/6335363, but made
        async to avoid blocking other tasks.

        Note that annoyingly, the history won't be applied unless VS Code is
        entirely closed during this step.
        """
        # Path should not be None, as if it was, this hook wouldn't be
        # registered
        assert path is not None
        log.info("Begin VS Code history cleanup")

        # Kinda painful that it's a database, not just a JSON file tbh
        state_path = (
            platformdirs.user_config_path()
            / "Code/User/globalStorage/state.vscdb"
        )
        log.info(f"VS Code state file should exist at {state_path}")

        # Create a backup copy
        state_backup = state_path.with_name("state-markten-backup.vscdb")
        _ = copyfile(state_path, state_backup)
        log.info(f"Created backup of VS Code state at {state_backup}")

        try:
            async with aiosqlite.connect(state_path) as db:
                cursor = await db.execute(
                    "SELECT [value] FROM ItemTable WHERE  [key] = "
                    + "'history.recentlyOpenedPathsList'"
                )
                history_raw = await cursor.fetchone()
                assert history_raw
                history: list[VsCodeHistoryEntry] = json.loads(history_raw[0])[
                    "entries"
                ]

                def should_keep_entry(e: VsCodeHistoryEntry) -> bool:
                    assert path is not None
                    uri = e.get("folderUri", e.get("fileUri"))
                    if uri is None:
                        return True
                    else:
                        uri = uri.removeprefix("file://")
                        keep = Path(uri) != path.absolute()
                        if not keep:
                            log.info(f"Remove history entry '{uri}'")
                        return keep

                # Remove this path from history
                new_history = [
                    item for item in history if should_keep_entry(item)
                ]

                # Then save it back out to VS Code
                new_history_str = json.dumps({"entries": new_history})
                _ = await db.execute(
                    "UPDATE ItemTable SET [value] = ? WHERE key = "
                    + "'history.recentlyOpenedPathsList'",
                    (new_history_str,),
                )
                await db.commit()
                log.info("VS Code history removal success")
        except BaseException:
            log.exception(
                "Error while updating VS Code state, reverting to back-up"
            )
            _ = copyfile(state_backup, state_path)
            # Continue error propagation
            raise

    if remove_history and path:
        action.add_teardown_hook(cleanup_vscode_history)
    return action


@markten_action
async def zed(
    action: ActionSession,
    path: Path | None = None,
):
    """
    Launch a new Zed window at the given Path.
    """
    # -n = new window
    # -w = CLI waits for window exit
    _ = await process.run(
        action.make_child(process.run),
        "zed",
        "-nw",
        *([str(path)] if path else []),
    )