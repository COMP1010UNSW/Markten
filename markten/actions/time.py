"""
# MarkTen / Actions / time.py

Actions for managing timing
"""

import asyncio
import time
from typing import Any

from markten.__spinners import SpinnerTask

from .__action import MarkTenAction


class sleep(MarkTenAction):
    """
    Action that waits for the given amount of time.
    """

    def __init__(self, duration: float) -> None:
        """Pause execution for the given duration.

        Equivalent to a `time.sleep()` call, but without blocking other
        actions.

        Parameters
        ----------
        duration : float
            Time to pause, in seconds.
        """
        self.duration = duration

    def get_name(self) -> str:
        return f"sleep {self.duration}"

    async def run(self, task: SpinnerTask) -> Any:
        task.running()

        start_time = time.time()
        now = time.time()

        while now - start_time < self.duration:
            # Give a countdown
            remaining = self.duration - (now - start_time)
            task.message(f"{round(remaining)}s remaining...")
            if remaining > 1:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(remaining)
            now = time.time()

        task.succeed("0s remaining")

    async def cleanup(self) -> None: ...
