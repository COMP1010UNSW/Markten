"""
# MarkTen / Actions / fs.py

Actions associated with the file system.
"""

from pathlib import Path

from aiofiles import tempfile as a_tempfile

from markten import ActionSession


async def temp_dir(action: ActionSession) -> Path:
    """Create a temporary directory, yielding its path."""
    action.message("Creating temporary directory")
    temp_dir_cm = a_tempfile.TemporaryDirectory(prefix="markten")

    # Need to manually open the file, as per
    # https://github.com/Tinche/aiofiles/issues/161#issuecomment-1974852636
    action.add_teardown_hook(lambda: temp_dir_cm.__aexit__(None, None, None))

    file_path = await temp_dir_cm.__aenter__()
    action.succeed(file_path)
    return Path(file_path)
