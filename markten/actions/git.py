"""
# MarkTen / Actions / git.py

Actions associated with `git` and Git repos.
"""
from logging import Logger
from pathlib import Path

from markten.__utils import TextCollector
from .__async_process import run_process

from .__action import MarkTenAction


log = Logger(__name__)


class clone(MarkTenAction):
    """
    Perform a `git clone` operation.
    """

    def __init__(self, repo_url: str, /, branch: str | None = None) -> None:
        self.repo = repo_url
        self.branch = branch

    def get_name(self) -> str:
        return "git clone"

    async def run(self, task) -> Path:
        # Make a temporary directory
        task.message("Creating temporary directory")

        clone_path = TextCollector()

        if await run_process(
            ("mktemp", "--directory"),
            on_stdout=clone_path,
            on_stderr=task.log,
        ):
            task.fail("mktemp failed")
            raise RuntimeError("mktemp failed")

        # Perform the git clone
        if self.branch:
            branch_args = ["-b", self.branch, "--single-branch"]
        else:
            branch_args = []

        program = ("git", "clone", *branch_args, self.repo, str(clone_path))
        task.running(' '.join(program))

        clone = await run_process(
            program,
            on_stderr=task.log,
        )
        if clone:
            task.fail(f"git clone exited with error code: {clone}")
            raise Exception("Task failed")

        task.succeed(f"Cloned {self.repo} to {clone_path}")
        return Path(str(clone_path))

    async def cleanup(self) -> None:
        # Temporary directory will be automatically cleaned up by the OS, so
        # there is no need for us to do anything
        return
