"""
tests / parameters / stdin_test
==================================

Test cases for the `stdin` parameter.
"""

import io

import pytest

from markten.parameters import stdin


def test_stdin_basic(monkeypatch: pytest.MonkeyPatch):
    """
    Basic test mocking stdin
    """
    monkeypatch.setattr("sys.stdin", io.StringIO("a\nb\nc"))

    assert list(stdin("test")) == ["a", "b", "c"]


def test_repeat_stdin(monkeypatch: pytest.MonkeyPatch):
    """
    When the iterable is repeated, it should re-use previous values.
    """
    monkeypatch.setattr("sys.stdin", io.StringIO("a\nb\nc"))

    it = stdin("test", repeat_values=True)
    assert list(it) == ["a", "b", "c"]
    assert list(it) == ["a", "b", "c"]
