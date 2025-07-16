"""
# Markten / Recipe / Step

A single step within a recipe.
"""

import asyncio
import inspect
from typing import Any, TypeVar

from rich.live import Live

from markten.__action_session import ActionSession, TeardownHook
from markten.__cli import CliManager
from markten.__consts import TIME_PER_CLI_FRAME
from markten.actions.__action import MarktenAction, ResultType

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
        with Live(refresh_per_second=1/TIME_PER_CLI_FRAME) as live:
            spinners = CliManager(live)
            session = ActionSession(self.__name)

            # Now await all yielded values
            tasks: list[asyncio.Task[Any]] = []
            for action in self.__actions:
                tasks.append(asyncio.create_task(call_action_with_context(
                    action,
                    parameters | state,
                    session.make_child(action),
                )))

            # Start drawing the spinners
            spinner_task = asyncio.create_task(spinners.run(session))
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

            session.succeed()
            # Stop spinners
            spinners.stop()
            await spinner_task

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


def dict_to_actions(
    actions: dict[str, MarktenAction[ResultType]],
) -> list[MarktenAction[ResultType]]:
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
    for name, fn in actions.items():

        def make_generator(name, fn):
            """
            Make the generator function.

            Needed to capture the `name` and `fn` loop variables, else they
            will end up being the last value of the iteration.

            https://docs.astral.sh/ruff/rules/function-uses-loop-variable/
            """

            async def generator(
                task: ActionSession, **kwargs
            ) -> dict[str, ResultType]:
                """The actual generator function"""
                gen = call_action_with_context(fn, kwargs, task)
                return {name: await gen}

            return generator

        result.append(make_generator(name, fn))

    return result
