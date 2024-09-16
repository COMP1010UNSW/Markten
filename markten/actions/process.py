"""
# MarkTen / Actions / process.py

Actions for running subprocesses
"""
import asyncio
from logging import Logger
from .__action import MarkTenAction


log = Logger(__name__)


class run(MarkTenAction):
    """
    Run the given process for the duration of this step of the recipe.
    """

    def __init__(self, *args: str) -> None:
        self.args = args

        self.process: asyncio.subprocess.Process | None = None

    async def begin(self) -> None:
        self.process = await asyncio.create_subprocess_exec(
            *self.args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def end(self) -> None:
        assert self.process is not None
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
