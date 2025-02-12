"""
tests / parameters / list_dir_test
==================================

Test cases for the `list_dir` parameter.
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from markten.parameters import list_dir


def test_lists_dir():
    """
    Basic test case
    """
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "a").touch()
        (tmp / "b").touch()
        assert list(list_dir(tmp)) == [
            tmp / "a",
            tmp / "b",
        ]


def test_filter_dirs_only():
    """
    Skips files when `directories=True`
    """
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "a").mkdir()
        (tmp / "b").touch()
        assert list(list_dir(tmp, directories=True)) == [tmp / "a"]


def test_filter_files_only():
    """
    Skips directories when `files=True`
    """
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "a").mkdir()
        (tmp / "b").touch()
        assert list(list_dir(tmp, files=True)) == [tmp / "b"]


def test_filter_hidden_dotfiles():
    """
    Skips files that begin with a `.`, as these are hidden on POSIX systems.
    """
    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / ".hidden").touch()
        assert list(list_dir(tmp, skip_hidden=True)) == []


@pytest.mark.skipif(os.name != "nt", reason="Windows-only")
def test_filter_hidden_windows():
    """
    Skips hidden files that have a hidden attribute on Windows.
    """
    import win32api
    import win32con

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "hidden").touch()
        # Mark dir as hidden
        # https://stackoverflow.com/a/43441935/6335363
        win32api.SetFileAttributes(
            str(tmp / "hidden"),
            win32con.FILE_ATTRIBUTE_HIDDEN,
        )
        assert list(list_dir(tmp, skip_hidden=True)) == []


def test_custom_filter():
    """
    Skips files that don't pass custom filter function
    """

    def filter_fn(p: Path) -> bool:
        return p.name == "a"

    with TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        (tmp / "a").touch()
        (tmp / "b").touch()
        assert list(list_dir(tmp, filter_fn)) == [
            tmp / "a",
        ]
