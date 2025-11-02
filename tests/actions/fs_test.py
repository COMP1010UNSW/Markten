"""
tests / actions / fs_test.py

Test cases for file system operations
"""

import pytest

from markten import ActionSession
from markten.actions import fs


@pytest.mark.asyncio
async def test_read_write_file():
    action = ActionSession("test")
    dir = await fs.temp_dir(action)

    await fs.write_file(action, dir / "file", "Some text")

    assert await fs.read_file(action, dir / "file") == "Some text"


@pytest.mark.asyncio
async def test_cannot_overwrite_file():
    action = ActionSession("test")
    dir = await fs.temp_dir(action)

    await fs.write_file(action, dir / "file", "Some text")

    with pytest.raises(FileExistsError):
        await fs.write_file(action, dir / "file", "Some text")


@pytest.mark.asyncio
async def test_force_overwrite_file():
    action = ActionSession("test")
    dir = await fs.temp_dir(action)

    await fs.write_file(action, dir / "file", "Some text")

    await fs.write_file(action, dir / "file", "Some text", overwrite=True)
