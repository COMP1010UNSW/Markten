"""
# Markten / Actions / editor / vs_code

Code for managing the VS Code text editor.
"""

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, cast

from markten.__action_session import ActionSession
from markten.__utils import link_file, unlink_file
from markten.actions import process
from markten.actions.__action import markten_action
from markten.actions.editor.__interface import TextEditorAction

log = logging.getLogger(__name__)


def code_alike(executable_name: str):
    """
    Make a VSCode-alike editor implementation.

    Parameters
    ----------
    executable_name
    """

    @markten_action
    async def code(
        action: ActionSession,
        *paths: Path,
        remove_history: bool = False,
        snippets: Path | None = None,
    ):
        """
        Launch a new Code window with the given paths.

        Parameters
        ----------
        action : ActionSession
            Action session
        paths : *Path
            Paths to open in VS Code.
        remove_history : bool
            Whether to prevent the opened locations from being added to VS
            Code's history. Defaults to `False`.
        snippets : Path
            Paths to a VS Code snippets file. It will be copied to the project
            directory while VS Code is open, and deleted once it exits. The
            snippets file must be a global snippet file (ie not
            language-specifics) such that it can be configured to not conflict
            with existing snippet files.
            https://code.visualstudio.com/docs/editing/userdefinedsnippets#_project-snippet-scope
        """
        # If there is a snippet file, copy it to the given path
        snippet_targets: list[Path] = []
        if snippets:
            for p in paths:
                snippet_dir = p / ".vscode"
                snippet_file = "markten.code-snippets"
                n = 0
                while (snippet_dir / snippet_file).exists():
                    n += 1
                    snippet_file = f"markten-{n}.code-snippets"

                target = snippet_dir / snippet_file
                snippet_targets.append(target)
                target.parent.mkdir(parents=True, exist_ok=True)
                await link_file(snippets, target)

        # -n = new window
        # -w = CLI waits for window exit
        flags = ["-n", "-w"]

        if remove_history:
            # An undocumented command-line flag! Lovely!
            # https://github.com/microsoft/vscode/issues/245122
            flags.append("--skip-add-to-recently-opened")

        _ = await process.run(
            action.make_child(process.run),
            executable_name,
            *flags,
            *[str(p) for p in paths],
        )

        # After VS Code exits, we may need to remove the snippet
        # This is not a teardown step, since we don't want to accidentally
        # commit it
        async with asyncio.TaskGroup() as tg:
            for snip in snippet_targets:
                _ = tg.create_task(unlink_file(snip))

    return code


vs_code = code_alike("code")
vs_codium = code_alike("codium")


if TYPE_CHECKING:
    validate_calling_behaviour: TextEditorAction = cast(
        TextEditorAction, vs_code
    )
    _ = validate_calling_behaviour(ActionSession(""), Path("foo"), Path("foo"))

    # Basedpyright is not happy with this, but mypy is. It seems correct from
    # my checking.
    validate_type_compatibility: TextEditorAction = vs_code
