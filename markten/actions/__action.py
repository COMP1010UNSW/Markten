from collections.abc import AsyncGenerator, Callable
from typing import Any

from markten.__recipe.step import run_to_completion, start_generator
from markten.__spinners import SpinnerTask

ActionResult = Any | dict[str, Any]
"""
Result from a Markten action.

Either a single value or a dict mapping from parameter names to their
corresponding values.

* Single values with no name will be discarded if used directly as a step.
* Dict values will be added to the `context` for future steps.
"""

ActionGenerator = AsyncGenerator[ActionResult, None]
"""
A partially-executed action -- essentially a generator function which will
yield a new state.
"""

MarktenAction = Callable[..., AsyncGenerator[ActionResult, None]]
"""
A Markten action is an async generator function which optionally yields a state
to be used in future steps.

It is called, with the `anext` function being used to execute the action. Once
the function evaluates, it should yield a new state. Any required clean-up
should be written after this `yield`. The generator should only `yield` one
value. All other values will be ignored.
"""


def dict_to_actions(action: dict[str, MarktenAction]) -> list[MarktenAction]:
    """Convert the given dictionary of actions into a list of actions.

    All the given actions will be run in parallel.

    Parameters
    ----------
    action : dict[str, MarktenAction]
        Action dictionary

    Returns
    -------
    list[MarktenAction]
        Each action in the dictionary as its own independent action.
    """
    result = []
    for name, fn in action.items():

        def make_generator(name, fn):
            """
            Make the generator function.

            Needed to capture the `name` and `fn` loop variables, else they
            will end up being the last value of the iteration.

            https://docs.astral.sh/ruff/rules/function-uses-loop-variable/
            """

            async def generator(
                task: SpinnerTask, **kwargs
            ) -> ActionGenerator:
                """The actual generator function"""
                gen = start_generator(fn, kwargs, task)
                yield {name: await anext(gen)}
                await run_to_completion(gen)

            return generator

        result.append(make_generator(name, fn))

    return result
