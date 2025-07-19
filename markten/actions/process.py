"""
# Markten / Actions / process.py

Actions for running subprocesses
"""

import asyncio
import signal
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import Any
from warnings import deprecated

from markten import ActionSession
from markten.__utils import TextCollector
from markten.actions import fs

from .__async_process import run_process

log = Logger(__name__)


async def run(
    action: ActionSession,
    *args: str,
    allow_exit_failure: bool = False,
) -> int:
    """Run the given process, and wait for it to exit before resolving.

    Parameters
    ----------
    action : ActionSession
        Action session
    *args : str
        Program to execute.
    allow_exit_failure : bool, optional
        Whether to fail the action if the process exits with a non-zero status
        code, by default False

    Returns
    -------
    int
        Subprocess's exit code.
    """
    action.running(" ".join(args))
    returncode = await run_process(
        args,
        on_stdout=action.log,
        on_stderr=action.log,
    )
    if returncode and not allow_exit_failure:
        raise RuntimeError(f"Process exited with code {returncode}")
    action.succeed()
    return returncode


async def run_stdout(
    action: ActionSession,
    *args: str,
    allow_exit_failure: bool = False,
) -> str:
    """Run the given process, wait for it to exit, and resolve with its stdout
    output.

    Parameters
    ----------
    action : ActionSession
        Action session
    allow_exit_failure : bool, optional
        Whether to fail the action if the process exits with a non-zero status
        code, by default False

    Returns
    -------
    str
        Process stdout
    """
    action.running(" ".join(args))
    stdout = TextCollector()
    returncode = await run_process(
        args,
        on_stdout=stdout,
        on_stderr=action.log,
    )
    if returncode and not allow_exit_failure:
        raise RuntimeError(f"Process exited with code {returncode}")
    action.succeed()
    return str(stdout)


async def run_in_background(
    action: ActionSession,
    *args: str,
    exit_timeout: float = 2,
) -> tuple[Path, Path]:
    """Run the given process in the background, only killing it during the
    tear-down phase.

    This is useful for actions such as spinning up a web server for the
    duration of marking.

    Parameters
    ----------
    action : ActionSession
        Action session context.
    *args : str
        Program to execute.
    exit_timeout : float, optional
        Number of seconds to wait after interrupting process with SIGINT before
        forcefully killing it using SIGKILL, by default 2.

    Returns
    -------
    tuple[Path, Path]
        File paths for stdout and stderr of subprocess.
    """
    temp = await fs.temp_dir(action.make_child(fs.temp_dir))

    stdout = temp / "stdout"
    stderr = temp / "stderr"

    # Open files to pass as stdout and stderr for subprocess
    f_stdout = open(stdout)  # noqa: SIM115
    f_stderr = open(stderr)  # noqa: SIM115

    action.running(" ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=f_stdout,
        stderr=f_stderr,
    )

    async def cleanup():
        # If program hasn't quit already
        if process.returncode is None:
            # Interrupt
            process.send_signal(signal.SIGINT)
            # Wait for process to exit
            try:
                await asyncio.wait_for(process.wait(), exit_timeout)
            except TimeoutError:
                process.kill()
                log.error("Subprocess failed to exit in given timeout window")

        # Close handles for stdout and stderr
        f_stdout.close()
        f_stderr.close()

    action.add_teardown_hook(cleanup)

    return stdout, stderr


run_async = deprecated("Use `run_in_background` instead")(run_in_background)


async def run_detached(
    action: ActionSession,
    *args: str,
) -> tuple[Path, Path]:
    """Run the given process, but detach it such that it won't exit, even after
    the markten recipe finishes.

    This is useful for launching GUI applications when you don't want to kill
    them when finishing a recipe permutation.

    Parameters
    ----------
    action : ActionSession
        Action session.
    *args : str
        Program to execute.

    Returns
    -------
    tuple[Path, Path]
        File paths for stdout and stderr of subprocess.
    """
    temp = await fs.temp_dir(action.make_child(fs.temp_dir))

    stdout = temp / "stdout"
    stderr = temp / "stderr"

    # Open files to pass as stdout and stderr for subprocess
    f_stdout = open(stdout)  # noqa: SIM115
    f_stderr = open(stderr)  # noqa: SIM115

    action.running(" ".join(args))

    if sys.platform == "win32":
        # On Windows, we need a specific subprocess flag
        # Need to type it as `dict[str, Any]` or mypy freaks out
        options: dict[str, Any] = {
            # https://stackoverflow.com/a/78852901/6335363
            "creationflags": subprocess.DETACHED_PROCESS,
        }
    else:
        # Assume system is unix-y
        options: dict[str, Any] = {
            # https://stackoverflow.com/a/64145368/6335363
            "start_new_session": True,
        }

    subprocess.Popen(
        args,
        stdout=f_stdout,
        stderr=f_stderr,
        **options,
    )
    return stdout, stderr
