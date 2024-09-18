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

    async def run(self, spinners) -> Path:
        # Make a temporary directory
        task = spinners.create_task(self, "git clone")

        task.message("Creating temporary directory")

        mktemp = await asyncio.create_subprocess_exec(
            "mktemp",
            "--directory",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await mktemp.communicate()
        if mktemp.returncode:
            task.fail("mktemp failed")
            raise RuntimeError("mktemp failed")

        clone_path = Path(stdout.decode().strip())
        task.running("Cloning repository")

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
            clone_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await clone.communicate()
        if clone.returncode:
            task.fail(f"git clone exited with error code: {clone.returncode}")

        task.succeed(f"Cloned to {clone_path}")
        return clone_path

    async def cleanup(self) -> None:
        # Temporary directory will be automatically cleaned up by the OS, so
        # there is no need for us to do anything
        return
