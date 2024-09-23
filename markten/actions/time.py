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
    Waits for the given duration.
    """

    def __init__(self, duration: float) -> None:
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

        task.succeed('0s remaining')

    async def cleanup(self) -> None:
        ...
