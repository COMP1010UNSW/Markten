"""
# MarkTen / Utils

Utility functions.
"""

import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from . import __consts as consts


def relativize_file(file: Path, to: Path | None = None) -> Path:
    """
    Return file path relative to given dir, or cwd
    """
    if to is None:
        to = Path(os.getcwd())

    if file.is_relative_to(to):
        return file.relative_to(to)
    else:
        return file


def recipe_banner(
    recipe_name: str | None,
    recipe_file: str | None,
) -> None:
    """Display a banner to the console for the given recipe

    Parameters
    ----------
    recipe_name : str | None
        Name of recipe
    recipe_file : str | None
        File of recipe
    """
    console = Console()

    text = []
    if recipe_name:
        text.append(f"Recipe: [cyan]{recipe_name}[/]")
    if recipe_file:
        text.append(f"File: [cyan]{relativize_file(Path(recipe_file))}[/]")

    panel = Panel("\n".join(text), title=f"MarkTen v{consts.VERSION}")
    console.print(panel)


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
        return "\n".join(self.__output).strip()
