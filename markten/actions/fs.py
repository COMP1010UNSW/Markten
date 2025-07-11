"""
# MarkTen / Actions / fs.py

Actions associated with the file system.
"""

from collections.abc import Awaitable, Callable
from pathlib import Path

from aiofiles import tempfile as a_tempfile

from .__action import MarkTenAction


class tempfile(MarkTenAction):
    """
    Create a temporary file or directory.
    """

    def __init__(self, /, directory: bool = False) -> None:
        """Create a temporary file or directory, yielding its name.

        _extended_summary_

        Parameters
        ----------
        directory : bool, optional
            _description_, by default False
        """
        self.directory = directory
        self.file = None
        """Reference to temporary file"""
        self._close: None | Callable[[], Awaitable[None]] = None

    def get_name(self) -> str:
        return "tempfile"

    async def run(self, task) -> Path:
        if self.directory:
            task.message("Creating temporary directory")
            self.file = await a_tempfile.TemporaryDirectory(prefix="markten")  # type: ignore
            # Intentionally ignoring type errors -- they'll go away when I
            # rewrite to use async generators
            self._close = self.file.close  # type: ignore
        else:
            task.message("Creating temporary directory")
            self.file = await a_tempfile.NamedTemporaryFile(prefix="markten")  # type: ignore

        return Path(str(self.file.name))  # type: ignore

    async def cleanup(self) -> None:
        if self._close is not None:
            await self._close()
            self._close = None
