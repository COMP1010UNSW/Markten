"""
# MarkTen / Main

Programmatic entrypoint to MarkTen, allowing it to be run as a script.
"""

import os
import sys

import click

from . import __consts as consts

HELP_STR = """
Markten -- Assess your students' work with all of the delight and none of the
tedium.

View the documentation for information on writing recipes:
https://github.com/COMP1010UNSW/MarkTen
"""


@click.command("markten", help=HELP_STR)
@click.argument("recipe", type=click.Path(exists=True, readable=True))
@click.argument("args", nargs=-1)
@click.version_option(consts.VERSION)
def main(recipe: str, args: tuple[str, ...]):
    os.execv(sys.executable, ("python", recipe, *args))


if __name__ == "__main__":
    main()
