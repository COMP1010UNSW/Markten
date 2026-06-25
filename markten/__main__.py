"""
# Markten / Main

Programmatic entrypoint to Markten, allowing it to be run as a script.
"""

import runpy
import sys

import click
import rich
from rich.panel import Panel

from markten.__context import get_context

from . import __consts as consts
from . import __utils as utils

console = rich.get_console()

title = f"Markten - v{consts.VERSION}"

help_text = f"""
✅  Assess your students' work with all of the [green]delight[/] and none of the [red]tedium[/]

Usage: [bold magenta]markten [OPTIONS] RECIPE [ARGS]...[/]

Options:
  [yellow]-v, --verbose[/]  Increase the verbosity of markten's output.
                 You can also set this using '[yellow]{consts.VERBOSE_ENV_VAR}[/]' environment variable.

  [yellow]--version[/]      Show the version and exit.
  [yellow]--help[/]         Show this message and exit.

[bold yellow]RECIPE[/]: Recipe program to execute.

[bold yellow][ARGS][/]: Additional program arguments, passed to recipe program.

Made with [magenta]<3[/] by Maddy Guthridge

View the project on GitHub: [cyan]https://github.com/COMP1010UNSW/Markten[/]
View the documentation: [cyan]https://github.com/COMP1010UNSW/Markten[/]
""".strip()  # noqa: E501


def show_help(ctx: click.Context, param: click.Option, value: bool):
    if not value or ctx.resilient_parsing:
        return
    console.print(Panel(help_text, title=title, border_style="blue"))
    ctx.exit()


@click.command("markten", help=help_text)
@click.option(
    "--help",
    is_flag=True,
    callback=show_help,
    expose_value=False,
    is_eager=True,
)
@click.option("-v", "--verbose", count=True, envvar=consts.VERBOSE_ENV_VAR)
@click.argument("recipe", type=click.Path(exists=True, readable=True))
@click.argument("args", nargs=-1)
@click.version_option(consts.VERSION)
def main(recipe: str, args: tuple[str, ...], verbose: int = 0):
    # Set verbosity
    get_context().verbosity = verbose
    # replace argv
    sys.argv = [sys.argv[0], *args]
    try:
        # Then run code as main
        _ = runpy.run_path(recipe, {}, "__main__")
    except Exception as e:
        utils.print_exception(str(e), get_context().verbosity)
        exit(1)


if __name__ == "__main__":
    main()
