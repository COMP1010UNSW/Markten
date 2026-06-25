"""
# Markten / recipe / hook

Code for running hooks.
"""

from collections.abc import Awaitable, Callable
from typing import ParamSpec

import rich

from markten import __utils as utils
from markten.__context import get_context

console = rich.get_console()


P = ParamSpec("P")


async def exec_hook(
    hook: Callable[P, None | Awaitable[None]],
    *args: P.args,
    **kwargs: P.kwargs,
):
    """
    Execute the given hook function.

    * If the hook returns an awaitable, await it.
    * If the hook throws an exception, consume and log it.
    """
    try:
        result = hook(*args, **kwargs)
        if isinstance(result, Awaitable):
            await result
    except Exception:
        utils.print_exception(
            "An error occured while running a hook",
            get_context().verbosity,
        )
