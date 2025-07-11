"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""

import asyncio
import signal
from collections.abc import Callable, Coroutine
from logging import Logger
from typing import Any

from markten.__spinners import SpinnerTask

from .__action import ActionGenerator
from .__async_process import run_process

log = Logger(__name__)


async def run(
    task: SpinnerTask,
    *args: str,
    allow_exit_failure: bool = False,
) -> ActionGenerator:
    task.running()
    returncode = await run_process(
        args,
        on_stdout=task.log,
        on_stderr=task.log,
    )
    if returncode and not allow_exit_failure:
        task.fail(f"Process exited with code {returncode}")
        raise RuntimeError("process.run: action failed")
    task.succeed()
    yield returncode


CleanupHook = Callable[[], Coroutine[Any, Any, Any]]


async def run_async(
    task: SpinnerTask,
    *args: str,
    exit_timeout: float = 2,
) -> ActionGenerator:
    task.running(" ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    task.succeed()

    yield

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
