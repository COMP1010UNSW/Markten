"""
# Markten / Actions / git.py

Actions associated with `git` and Git repos.
"""

from . import __gitlab as gitlab
from .__git import (
    add,
    branch_exists,
    checkout,
    clone,
    commit,
    current_branch,
    pull,
    push,
)

__all__ = [
    "add",
    "branch_exists",
    "checkout",
    "clone",
    "commit",
    "current_branch",
    "pull",
    "push",
    "gitlab",
]
