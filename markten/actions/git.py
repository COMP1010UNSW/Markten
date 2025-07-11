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

DEFAULT_REMOTE = "origin"


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
        """Perform a `git clone` operation.

        By default, this clones the project to a temporary directory.

        Parameters
        ----------
        repo_url : str
            URL to clone
        branch : str | None, optional
            Branch to checkout after cloning is complete, by default None
        fallback_to_main : bool, optional
            Whether to fall back to the main branch if the given branch does
            not exist, by default False
        dir : str | None, optional
            Directory to clone to, by default None for a temporary directory
        """
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
                "-C",
                clone_path,
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


class checkout(MarkTenAction):
    """
    Perform a `git checkout` operation on an existing repository.
    """

    def __init__(
        self,
        dir: Path,
        branch_name: str,
        /,
        create: bool = False,
        push_to_remote: str | bool = False,
    ) -> None:
        """Perform a `git checkout` operation.

        This changes the active branch for the given git repository.

        Parameters
        ----------
        dir : Path
            Path to git repository
        branch_name : str
            Branch to checkout
        create : bool, optional
            Whether to pass a `-b` flag to the `git checkout` operation,
            signalling that `git` should create a new branch.
        push_to_remote : str | bool, optional
            Whether to also push this branch to the given remote. This
            requires the `create` flag to also be `True`. If `True` is given,
            this will create the branch on the `origin` remote. Otherwise, if a
            `str` is given, this will push to that remote.
        """
        self.dir = dir
        self.branch_name = branch_name
        self.create = create
        self.push_to_remote = push_to_remote

        if push_to_remote is not None and not create:
            raise ValueError(
                "MarkTen.actions.git.checkout: Cannot specify "
                "`push_to_remote` if `create is False`"
            )

    def get_name(self) -> str:
        return "git checkout"

    async def run(self, task) -> None:
        program: tuple[str, ...] = (
            "git",
            "-C",
            str(self.dir),
            "checkout",
            *(("-b") if self.create else ()),
            self.branch_name,
        )
        task.running(" ".join(program))

        checkout = await run_process(
            program,
            on_stderr=task.log,
        )
        if checkout:
            error = f"git checkout exited with error code: {checkout}"
            task.fail(error)
            raise Exception(error)

        if self.push_to_remote is not False:
            program = (
                "git",
                "-C",
                str(self.dir),
                "push",
                "--set-upstream",
                self.push_to_remote
                if isinstance(self.push_to_remote, str)
                else DEFAULT_REMOTE,
                self.branch_name
            )
            task.running(" ".join(program))
            remote_create = await run_process(
                program,
                on_stderr=task.log,
            )
            if remote_create:
                error = (
                    f"git push --set-upstream exited with error code: "
                    f"{remote_create}")

                task.fail(error)
                raise Exception(error)

        task.succeed(
            f"Switched to{' new' if self.create else ''} "
            f"branch {self.branch_name}"
            + " and pushed to remote" if self.push_to_remote else ""
        )
