"""
# Markten / Recipe / Step

A single step within a recipe.
"""

import asyncio
import inspect
from typing import Any, TypeVar

from rich.live import Live

from markten.__action_session import ActionSession, TeardownHook
from markten.__cli import SpinnerManager
from markten.actions.__action import MarktenAction

T = TypeVar("T")


class RecipeStep:
    def __init__(
        self,
        index: int,
        name: str,
        actions: list[MarktenAction],
    ) -> None:
        self.__index = index
        self.__name = name
        self.__actions = actions

    async def run(
        self,
        parameters: dict[str, Any],
        state: dict[str, Any],
    ) -> tuple[dict[str, Any], list[TeardownHook]]:
        """Run this step of the recipe.

        This receives the parameters from the previous step, and produces a new
        dictionary with parameters for the next step.

        Parameters
        ----------
        parameters : dict[str, Any]
            Parameters to use for this permutation of the recipe.
        state : dict[str, Any]
            Named data produced from previous steps of the recipe. Data from
            this state is included in a new returned dictionary, and updated
            with return values from named actions in this step.

        Yields
        ------
        dict[str, Any]
            Data from this step, to use when running future steps.
        """
        with Live() as live:
            spinners = SpinnerManager(
                f"{self.__index + 1}. {self.__name}", live
            )
            session = ActionSession(self.__name, spinners.redraw)

            # Now await all yielded values
            tasks: list[asyncio.Task[Any]] = []
            for action in self.__actions:
                tasks.append(asyncio.create_task(call_action_with_context(
                    action,
                    parameters | state,
                    session.make_child(action),
                )))

            # Start drawing the spinners
            spinner_task = asyncio.create_task(spinners.spin())
            # Now wait for all tasks to resolve
            results: dict[str, Any] = {}
            task_errors: list[Exception] = []
            for task in tasks:
                try:
                    result = await task
                    if isinstance(result, dict):
                        # Add corresponding values to the results dict
                        for key, value in result.items():
                            results[key] = value
                except Exception as e:
                    task_errors.append(e)

            # Stop spinners
            spinner_task.cancel()

            if len(task_errors):
                raise ExceptionGroup(
                    f"Task failed on step {self.__index + 1}",
                    task_errors,
                )

        # Produce new state to next task
        return (state | results, session.get_teardown_hooks())


async def call_action_with_context(
    fn: MarktenAction[T],
    context: dict[str, Any],
    action: ActionSession,
) -> T:
    """Execute an action function, passing any required parameters as kwargs.

    Parameters
    ----------
    fn : MarktenAction
        Function to call to produce generator
    context : dict[str, Any]
        Context, including parameters and results of previous actions.
    action : ActionSession
        Action session, used to update status and provide logging.

    Returns
    -------
    ActionGenerator
        Return of that function, given its required parameters.
    """
    namespace = context | {"action": action}

    args = inspect.getfullargspec(fn)
    # Check if function uses kwargs
    kwargs_used = args[2] is not None
    if kwargs_used:
        # If so, pass the full namespace
        ret = await fn(**namespace)
    else:
        # Otherwise, only pass the args it requests
        named_args = args[0]
        param_subset = {
            name: value
            for name, value in namespace.items()
            if name in named_args
        }
        ret = await fn(**param_subset)
    # Succeed if not done already
    if not action.is_resolved():
        action.succeed()
    return ret
