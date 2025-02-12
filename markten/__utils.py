"""
# MarkTen / Utils

Utility functions.
"""
from typing import Any

from . import __consts as consts


def show_banner():
    print(f"== MarkTen | v{consts.VERSION} ==")


class TextCollector:
    """
    Collects text when called. When stringified, it produces the output, joined
    by newlines. With leading and trailing whitespace stripped.
    """

    def __init__(self) -> None:
        self.__output: list[str] = []

    def __call__(self, line: str) -> Any:
        self.__output.append(line)

    def __str__(self) -> str:
        return '\n'.join(self.__output).strip()
