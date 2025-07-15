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
    action: ActionSession,
    *args: str,
    allow_exit_failure: bool = False,
) -> int:
    action.running()
    returncode = await run_process(
        args,
        on_stdout=action.log,
        on_stderr=action.log,
    )
    if returncode and not allow_exit_failure:
        action.fail(f"Process exited with code {returncode}")
        raise RuntimeError("process.run: action failed")
    action.succeed()
    return returncode


async def run_async(
    action: ActionSession,
    *args: str,
    exit_timeout: float = 2,
) -> None:
    action.running(" ".join(args))
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    action.succeed()

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


    action.add_teardown_hook(cleanup)

