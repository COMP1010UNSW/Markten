"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""
import asyncio
import signal
from logging import Logger
from .__action import MarkTenAction


log = Logger(__name__)


class run(MarkTenAction):
    """
    Run the given process, and don't move to the next step until the process
    exits.
    """

    def __init__(self, *args: str) -> None:
        self.args = args

        self.process: asyncio.subprocess.Process | None = None

    async def run(self) -> None:
        self.process = await asyncio.create_subprocess_exec(
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await self.process.communicate()
        if self.process.returncode:
            log.error("\n".join([
                f"Subprocess {self.args[0]} exited with error code: {
                    self.process.returncode}",
                "stdout:",
                stdout.decode(),
                "stderr:",
                stderr.decode(),
            ]))
            raise RuntimeError("process.run: action failed")

    async def cleanup(self) -> None:
        # Nothing to do, task has already exited
        return


class run_parallel(MarkTenAction):
    """
    Run the given process until this step reaches the teardown phase. At that
    point, send a sigint.
    """

    def __init__(self, *args: str, exit_timeout: float = 2) -> None:
        self.args = args
        self.timeout = exit_timeout

        self.process: asyncio.subprocess.Process | None = None

    async def run(self) -> None:
        self.process = await asyncio.create_subprocess_exec(
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

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
