"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""

import asyncio
import signal
from collections.abc import Callable, Coroutine
from logging import Logger
from typing import Any

from .__action import MarkTenAction
from .__async_process import run_process

log = Logger(__name__)


CleanupHook = Callable[[], Coroutine[Any, Any, Any]]


class run(MarkTenAction):
    """
    Run the given process, waiting for it to exit before resolving the action.

    Additional hooks can be added to the cleanup process, for example to delete
    temporary files.
    """

    def __init__(self, *args: str, allow_nonzero: bool = False) -> None:
        """Run the given process, waiting for it to exit before resolving the
        action.

        If the process exits with a non-zero exit code, the task fails unless
        the `allow_nonzero` flag is given.

        Parameters
        ----------
        allow_nonzero : bool, optional
            Succeed the task, even if the process exited with a non-zero exit
            code, by default False
        """
        self.args = args
        self.cleanup_hooks: list[CleanupHook] = []

    def register_cleanup_hook(self, fn: CleanupHook):
        """Register a hook function to be executed after this task is complete.

        This should be an async function.

        Parameters
        ----------
        fn : CleanupHook
            Function to call on cleanup.
        """
        self.cleanup_hooks.append(fn)

    def get_name(self) -> str:
        return self.args[0]

    async def run(self, task) -> None:
        task.running()
        returncode = await run_process(
            self.args,
            on_stdout=task.log,
            on_stderr=task.log,
        )
        if returncode:
            task.fail(f"Process exited with code {returncode}")
            raise RuntimeError("process.run: action failed")
        task.succeed()

    async def cleanup(self) -> None:
        # Call cleanup hooks
        tasks = []
        for hook in self.cleanup_hooks:
            tasks.append(asyncio.create_task(hook()))


class run_parallel(MarkTenAction):
    """
    Run the given process until this step reaches the tear-down phase. At that
    point, send a sigint and wait for it to exit.
    """

    def __init__(self, *args: str, exit_timeout: float = 2) -> None:
        """Run the given process in parallel to the following steps. The
        process is interrupted during the cleanup phase.

        Parameters
        ----------
        exit_timeout : float, optional
            Maximum time to wait before forcefully quitting the subprocess, by
            default 2 seconds
        """
        self.args = args
        self.timeout = exit_timeout

        self.process: asyncio.subprocess.Process | None = None

    def get_name(self) -> str:
        return self.args[0]

    async def run(self, task) -> None:
        self.process = await asyncio.create_subprocess_exec(
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        task.succeed()

    async def cleanup(self) -> None:
        assert self.process is not None
        # If program hasn't quit already
        if self.process.returncode is None:
            # Interrupt
            self.process.send_signal(signal.SIGINT)
            # Wait for process to exit
            try:
                await asyncio.wait_for(self.process.wait(), self.timeout)
            except TimeoutError:
                self.process.kill()
                log.error("Subprocess failed to exit in given timeout window")
