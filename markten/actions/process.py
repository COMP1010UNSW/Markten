"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""

import asyncio
import signal
from logging import Logger

from markten import ActionSession

from .__async_process import run_process

log = Logger(__name__)


async def run(
    task: ActionSession,
    *args: str,
    allow_exit_failure: bool = False,
) -> int:
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
    return returncode


async def run_async(
    task: ActionSession,
    *args: str,
    exit_timeout: float = 2,
) -> None:
    task.running(" ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    task.succeed()

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


    task.add_teardown_hook(cleanup)

