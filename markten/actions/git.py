"""
# MarkTen / Actions / git.py

Actions associated with `git` and Git repos.
"""

from logging import Logger
from pathlib import Path
from typing import Any

from markten import ActionSession, MarktenAction
from markten.actions.fs import temp_dir

from .__async_process import run_process

log = Logger(__name__)

DEFAULT_REMOTE = "origin"


async def clone(
    task: ActionSession,
    repo_url: str,
    /,
    branch: str | None = None,
    fallback_to_main: bool = False,
    dir: Path | None = None,
) -> Path:
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
    dir : Path | None, optional
        Directory to clone to, by default None for a temporary directory
    """
    repo_url = repo_url.strip()
    branch = branch.strip() if branch else None

    if dir:
        clone_path = dir
    else:
        clone_path = await temp_dir(task.make_child(temp_dir))

    program: tuple[str, ...] = ("git", "clone", repo_url, str(clone_path))
    task.running(" ".join(program))

    clone = await run_process(
        program,
        on_stderr=task.log,
    )
    if clone:
        error = f"git clone exited with error code: {clone}"
        task.fail(error)
        raise Exception(error)

    if branch:
        program = (
            "git",
            "-C",
            str(clone_path),
            "checkout",
            "-b",
            branch,
            f"origin/{branch}",
        )
        task.running(" ".join(program))
        task.log(" ".join(program))
        checkout = await run_process(
            program,
            on_stderr=task.log,
        )
        if checkout:
            # Error when checking out branch
            if fallback_to_main:
                task.log("Note: remaining on main branch")
            else:
                error = f"Failed to check out to '{branch}'"
                task.fail(error)
                raise Exception(error)

    return clone_path


async def push(
    task: ActionSession,
    dir: Path,
    /,
    set_upstream: bool | str | tuple[str, str] = False,
):
    if not set_upstream:
        program = ("git", "-C", str(dir), "push")
        push = await run_process(program, on_stderr=task.log)
        if push:
            error = "Failed to push"
            task.fail(error)
            raise Exception(error)
        else:
            return None

    if set_upstream is True:
        remote = "origin"
        branch = "branch"
    elif isinstance(set_upstream, str):
        remote = "origin"
        branch = set_upstream
    else:
        remote, branch = set_upstream

    program = ("git", "-C", str(dir), "push", remote, branch)
    push = await run_process(program, on_stderr=task.log)
    if push:
        error = "Failed to push"
        task.fail(error)
        raise Exception(error)
    else:
        return None


async def pull(
    task: ActionSession,
    dir: Path,
) -> None:
    ...


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
                self.branch_name,
            )
            task.running(" ".join(program))
            remote_create = await run_process(
                program,
                on_stderr=task.log,
            )
            if remote_create:
                error = (
                    f"git push --set-upstream exited with error code: "
                    f"{remote_create}"
                )

                task.fail(error)
                raise Exception(error)

        task.succeed(
            f"Switched to{' new' if self.create else ''} "
            f"branch {self.branch_name}" + " and pushed to remote"
            if self.push_to_remote
            else ""
        )


class add(MarkTenAction):
    """
    Perform a `git add` operation on an existing repository.
    """

    def __init__(
        self,
        dir: Path,
        files: list[Path] | None = None,
        /,
        all: bool = False,
    ) -> None:
        """Perform a `git add` operation

        This stages the given list of changes, making them ready to commit.

        If the `files` list is empty and `all` is not specified, this will have
        no effect.

        Parameters
        ----------
        dir : Path
            Path to git repository.
        files : list[Path] | None, optional
            List of files to add, by default None, indicating that no files
            should be added.
        all : bool, optional
            whether to add all modified files, by default False

        Raises
        ------
        ValueError
            Files were specified when `all` is `True`
        """
        self.dir = dir
        self.files = files or []
        self.all = all

        if self.all and len(self.files):
            raise ValueError(
                "Should not specify files to commit when using the `all=True` "
                "flag."
            )

    async def run(self, task) -> Any:
        program: tuple[str, ...] = (
            "git",
            "-C",
            str(self.dir),
            "add",
            *(["-a"] if self.all else map(str, self.files)),
        )

        add = await run_process(
            program,
            on_stderr=task.log,
        )
        if add:
            error = f"git add exited with error code: {add}"
            task.fail(error)
            raise Exception(error)

        if self.all:
            task.succeed("Git: staged all files")
        else:
            task.succeed(f"Git: staged files {self.files}")


class commit(MarkTenAction):
    def __init__(
        self,
        dir: Path,
        message: str,
        /,
        all: bool = False,
        push: bool = False,
        files: list[Path] | None = None,
    ) -> None: ...


if __name__ == "__main__":
    __clone: MarktenAction = clone
