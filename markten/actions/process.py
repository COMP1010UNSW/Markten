"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""
import asyncio
import signal
from logging import Logger
from typing import Callable, Coroutine, Any
from .__action import MarkTenAction


log = Logger(__name__)


CleanupHook = Callable[[], Coroutine[Any, Any, Any]]


class run(MarkTenAction):
    """
    Run the given process, and don't move to the next step until the process
    exits.
    """

    def __init__(self, *args: str) -> None:
        self.args = args
        self.cleanup_hooks: list[CleanupHook] = []

    def register_cleanup_hook(self, fn: CleanupHook):
        self.cleanup_hooks.append(fn)

    def get_name(self) -> str:
        return self.args[0]

    async def run(self, task) -> None:
        task.running()
        process = await asyncio.create_subprocess_exec(
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode:
            task.fail(f"Process exited with code {process.returncode}")
            log.error("\n".join([
                f"Subprocess {self.args[0]} exited with error code: {
                    process.returncode}",
                "stdout:",
                stdout.decode(),
                "stderr:",
                stderr.decode(),
            ]))
            raise RuntimeError("process.run: action failed")
        task.succeed()

    async def cleanup(self) -> None:
        # Call cleanup hooks
        tasks = []
        for hook in self.cleanup_hooks:
            tasks.append(asyncio.create_task(hook()))


class run_parallel(MarkTenAction):
    """
    Run the given process until this step reaches the teardown phase. At that
    point, send a sigint.
    """

    def __init__(self, *args: str, exit_timeout: float = 2) -> None:
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
            except asyncio.TimeoutError:
                self.process.kill()
                log.error("Subprocess failed to exit in given timeout window")
