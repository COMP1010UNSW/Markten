"""
# MarkTen / Actions / fs.py

Actions associated with the file system.
"""

from pathlib import Path

from aiofiles import tempfile as a_tempfile

from markten.__spinners import SpinnerTask

from .__action import ActionGenerator


async def temp_dir(task: SpinnerTask) -> ActionGenerator[Path]:
    """Create a temporary directory, yielding its path."""
    task.message("Creating temporary directory")
    async with a_tempfile.TemporaryDirectory(prefix="markten") as f:
        yield Path(f)
