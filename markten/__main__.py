"""
# MarkTen / Main

Programmatic entrypoint to MarkTen, allowing it to be run as a script.
"""

import logging
import runpy
import sys

import click
from rich.console import Console
from rich.panel import Panel

from . import __consts as consts

console = Console()

title = f"MarkTen - v{consts.VERSION}"

help_text = """
✅  Assess your students' work with all of the [green]delight[/] and none of the [red]tedium[/]

Usage: [bold magenta]markten [OPTIONS] RECIPE [ARGS]...[/]

Options:
  [yellow]--version[/]  Show the version and exit.
  [yellow]--help[/]     Show this message and exit.

[bold yellow]RECIPE[/]: Recipe program to execute.

[bold yellow][ARGS][/]: Additional program arguments, passed to recipe program.

Made with [magenta]<3[/] by Maddy Guthridge

View the project on GitHub: [cyan]https://github.com/COMP1010UNSW/MarkTen[/]
View the documentation: [cyan]https://github.com/COMP1010UNSW/MarkTen[/]
""".strip()  # noqa: E501


def show_help(ctx: click.Context, param: click.Option, value: bool):
    if not value or ctx.resilient_parsing:
        return
    console.print(Panel(help_text, title=title, border_style="blue"))
    ctx.exit()


def handle_verbose(verbose: int):
    mappings = {
        0: "CRITICAL",
        1: "WARNING",
        2: "INFO",
        3: "DEBUG",
    }
    logging.basicConfig(level=mappings.get(verbose, "DEBUG"))


@click.command("markten", help=help_text)
@click.option(
    "--help",
    is_flag=True,
    callback=show_help,
    expose_value=False,
    is_eager=True,
)
@click.option("-v", "--verbose", count=True)
@click.argument("recipe", type=click.Path(exists=True, readable=True))
@click.argument("args", nargs=-1)
@click.version_option(consts.VERSION)
def main(recipe: str, args: tuple[str, ...], verbose: int = 0):
    handle_verbose(verbose)
    # replace argv
    sys.argv = [sys.argv[0], *args]
    # Then run code as main
    runpy.run_path(recipe, {}, "__main__")


if __name__ == "__main__":
    main()
