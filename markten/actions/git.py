"""
# MarkTen / Actions / git.py

Actions associated with `git` and Git repos.
"""
import asyncio
from logging import Logger
from pathlib import Path
from .__action import MarkTenAction


log = Logger(__name__)


class clone(MarkTenAction):
    """
    Perform a `git clone` operation.
    """

    def __init__(self, repo_url: str, /, branch: str | None = None) -> None:
        self.repo = repo_url
        self.branch = branch

        self.clone_path: Path | None = None

    async def begin(self) -> None:
        # Make a temporary directory
        mktemp = await asyncio.create_subprocess_exec(
            "mktemp",
            "--directory",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await mktemp.communicate()
        if mktemp.returncode:
            log.error("\n".join([
                f"mktemp exited with error code: {mktemp.returncode}",
                "stdout:",
                stdout.decode(),
                "stderr:",
                stderr.decode(),
            ]))
            raise RuntimeError("git clone action: mktemp failed")

        self.clone_path = Path(stdout.decode().strip())

        # Perform the git clone
        if self.branch:
            branch_args = ["-b", self.branch, "--single-branch"]
        else:
            branch_args = []

        clone = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            *branch_args,
            self.repo,
            self.clone_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await clone.communicate()
        if clone.returncode:
            log.error("\n".join([
                f"git clone exited with error code: {clone.returncode}",
                "stdout:",
                stdout.decode(),
                "stderr:",
                stderr.decode(),
            ]))
            raise RuntimeError("git clone action: clone failed")

    async def get_parameter(self) -> Path:
        assert self.clone_path is not None
        return self.clone_path

    async def end(self) -> None:
        # Temporary directory will be automatically cleaned up by the OS, so
        # there is no need for us to do anything
        return
