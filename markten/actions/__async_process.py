"""
# Markten / Actions / __async_process

Utility code for interacting with processes asynchronously.
"""

import asyncio
from collections.abc import Callable


async def read_stream(
    stream: asyncio.StreamReader,
    cb: Callable[[str], None],
) -> None:
    """Call the given callback for all lines of the given stream"""
    while True:
        line = await stream.readline()
        if line:
            cb(line.decode())
        else:
            break


async def run_process(
    cmd: tuple[str, ...],
    stdin: str = "",
    cwd: str | None = None,
    *,
    on_stdout: Callable[[str], None] | None = None,
    on_stderr: Callable[[str], None] | None = None,
) -> int:
    """
    Run a process, calling the given callbacks when receiving stdout and
    stderr.
    """
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stdin is not None
    process.stdin.write(stdin.encode())
    process.stdin.write_eof()

    assert process.stdout is not None
    assert process.stderr is not None

    async with asyncio.TaskGroup() as tg:
        if on_stdout:
            tg.create_task(read_stream(process.stdout, on_stdout))
        if on_stderr:
            tg.create_task(read_stream(process.stderr, on_stderr))
    return await process.wait()
