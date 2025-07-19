"""
# Markten / Actions / fs.py

Actions associated with the file system.
"""

from pathlib import Path

import aiofiles
import aiofiles.ospath
from aiofiles import tempfile as a_tempfile

from markten import ActionSession


async def temp_dir(action: ActionSession) -> Path:
    """Create a temporary directory, yielding its path."""
    action.message("Creating temporary directory")
    temp_dir_cm = a_tempfile.TemporaryDirectory(prefix="markten-")

    # Need to manually open/close the file, as per
    # https://github.com/Tinche/aiofiles/issues/161#issuecomment-1974852636
    action.add_teardown_hook(lambda: temp_dir_cm.__aexit__(None, None, None))

    file_path = await temp_dir_cm.__aenter__()
    action.succeed(file_path)
    return Path(file_path)


async def write_file(
    action: ActionSession,
    file: Path,
    text: str,
    /,
    overwrite: bool = False,
) -> None:
    """Write the given text into the given file.

    Unlike standard file management functions, this raises an exception if the
    file already exists, unless the `overwrite` option is given.

    Parameters
    ----------
    action : ActionSession
        Action session
    file : Path
        File to write into
    text : str
        Text to write
    overwrite : bool, optional
        Whether to overwrite the file if it already exists, by default False

    Raises
    ------
    FileExistsError
        File already exists.
    """
    if await aiofiles.ospath.exists(file) and not overwrite:
        raise FileExistsError(
            f"Cannot write into '{file}' as it already exists"
        )
    action.message(f"Writing {file}")
    async with aiofiles.open(file, "w") as f:
        await f.write(text)


async def read_file(action: ActionSession, file: Path) -> str:
    """Read text from the given file.

    Returns the text as a `str`.

    Parameters
    ----------
    action : ActionSession
        Action session
    file : Path
        File to read from.

    Returns
    -------
    str
        File contents.
    """
    action.message(f"Read {file}")
    async with aiofiles.open(file) as f:
        return await f.read()
