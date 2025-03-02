"""
# MarkTen / Actions / git.py

Actions associated with `git` and Git repos.
"""

from logging import Logger
from pathlib import Path

from markten.__spinners import SpinnerTask
from markten.__utils import TextCollector

from .__action import MarkTenAction
from .__async_process import run_process

log = Logger(__name__)


class clone(MarkTenAction):
    """
    Perform a `git clone` operation.
    """

    def __init__(
        self,
        repo_url: str,
        /,
        branch: str | None = None,
        fallback_to_main: bool = False,
        dir: str | None = None,
    ) -> None:
        self.repo = repo_url.strip()
        self.branch = branch.strip() if branch else None
        self.fallback_to_main = fallback_to_main
        self.dir = dir

    def get_name(self) -> str:
        return "git clone"

    async def mktemp(self, task: SpinnerTask) -> str:
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

        return str(clone_path)

    async def run(self, task) -> Path:
        clone_path = await self.mktemp(task) if self.dir is None else self.dir

        program: tuple[str, ...] = ("git", "clone", self.repo, clone_path)
        task.running(" ".join(program))

        clone = await run_process(
            program,
            on_stderr=task.log,
        )
        if clone:
            task.fail(f"git clone exited with error code: {clone}")
            raise Exception("Task failed")

        if self.branch:
            program = (
                "git",
                "checkout",
                "-b",
                self.branch,
                f"origin/{self.branch}",
            )
            task.running(" ".join(program))
            task.log(" ".join(program))
            checkout = await run_process(
                program,
                cwd=str(clone_path),
                on_stderr=task.log,
            )
            if checkout:
                # Error when checking out branch
                if self.fallback_to_main:
                    task.log("Note: remaining on main branch")
                else:
                    task.fail(f"Failed to check out to '{self.branch}'")
                    raise Exception("Task failed")

        task.succeed(f"Cloned {self.repo} to {clone_path}")
        return Path(clone_path)

    async def cleanup(self) -> None:
        # Temporary directory will be automatically cleaned up by the OS, so
        # there is no need for us to do anything
        return
