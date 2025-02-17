"""
# MarkTen / Recipe

Contains the definition for the main MarkTen class.
"""

import asyncio
import contextlib
import inspect
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from rich.live import Live

from . import __utils as utils
from .__spinners import SpinnerManager
from .actions import MarkTenAction
from .more_itertools import dict_permutations_iterator

ParameterType = Iterable[Any]
"""
Type of a MarkTen parameter.
"""

ParameterPermutations = Mapping[str, ParameterType]
"""
Mapping containing iterables for all permutations of the available params.
"""

GeneratedActions = (
    MarkTenAction | tuple[MarkTenAction, ...] | Mapping[str, MarkTenAction]
)
"""
`GeneratedActions` is a collection of actions run in parallel as a part of a
step in the marking recipe.

This can be one of:

* `MarkTenAction`: a single anonymous action, whose result is discarded.
* `tuple[MarkTenAction, ...]`: a collection of anonymous actions.
* `Mapping[str, MarkTenAction]`: a collection of named actions, whose results
  are stored as parameters under the given names.
"""

ActionGenerator = Callable[..., "ActionStep"]
"""
An `ActionGenerator` is a function that may accept any current parameters, and
must return an `ActionStep`, which is expanded recursively.
"""


ActionStepItem = ActionGenerator | GeneratedActions
"""
Each item in a step must either be a function that generates actions, or
pre-generated actions.
"""


ActionStep = ActionStepItem | tuple[ActionStepItem, ...]
"""
An `ActionStep` is a collection of items that should be executed in parallel.
"""

GeneratedActionStep = tuple[dict[str, MarkTenAction], list[MarkTenAction]]
"""
An `ActionStep` after running any action generators.

This is used internally when running the actions.

A tuple of:

* `dict[str, MarkTenAction]`: named actions
* `list[MarkTenAction]`: anonymous actions
"""


class Recipe:
    def __init__(
        self,
        recipe_name: str,
    ) -> None:
        # https://stackoverflow.com/a/13699329/6335363
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        self.__file = module.__file__ if module is not None else None
        self.__name = recipe_name
        self.__params: dict[str, ParameterType] = {}
        self.__steps: list[tuple[str, ActionStep]] = []

    def parameter(self, name: str, values: ParameterType) -> None:
        """
        Add a single parameter to the recipe.
        """
        self.__params[name] = values

    def parameters(self, parameters: ParameterPermutations) -> None:
        """
        Add a collection of parameters for the recipe.
        """
        self.__params |= dict(parameters)

    def step(self, name: str, step: ActionStep) -> None:
        """
        Add a step to the recipe
        """
        self.__steps.append((name, step))

    def run(self):
        """
        Run the marking recipe for each combination given by the generators.
        """
        asyncio.run(self.__do_run())

    async def __do_run(self):
        """Async implementation of running the marking recipe"""
        utils.recipe_banner(self.__name, self.__file)
        for params in dict_permutations_iterator(self.__params):
            # Begin marking with the given parameters
            show_current_params(params)
            # FIXME: Currently errors are eaten without a trace
            # Once logging is introduced, make them get logged
            with contextlib.suppress(Exception):
                await self.__run_recipe(params)
            print()

        print("Recipe ran for all inputs")

    async def __run_recipe(self, params: Mapping[str, Any]):
        """Execute the marking recipe using the given params"""
        params = dict(params)

        actions_by_step: list[GeneratedActionStep] = []
        """
        Actions ordered by step, used to ensure that we can run any required
        teardown at the end of the recipe.
        """
        for i, (name, step) in enumerate(self.__steps):
            # Convert the step into a list of actions to be run in parallel
            actions_to_run = generate_actions_for_step(step, params)
            actions_by_step.append(actions_to_run)

            with Live() as live:
                spinners = SpinnerManager(f"{i + 1}. {name}", live)

                # Run all tasks
                named_tasks: dict[str, asyncio.Task[Any]] = {}
                anonymous_tasks: list[asyncio.Task[Any]] = []
                # Named tasks
                for key, action in actions_to_run[0].items():
                    named_tasks[key] = asyncio.create_task(
                        action.run(spinners.create_task(action.get_name()))
                    )
                # Anonymous tasks
                for action in actions_to_run[1]:
                    anonymous_tasks.append(
                        asyncio.create_task(
                            action.run(spinners.create_task(action.get_name()))
                        )
                    )
                # Start drawing the spinners
                spinner_task = asyncio.create_task(spinners.spin())
                # Now wait for them all to resolve
                results: dict[str, Any] = {}
                task_errors: list[Exception] = []
                for key, task in named_tasks.items():
                    try:
                        results[key] = await task
                    except Exception as e:
                        task_errors.append(e)
                for task in anonymous_tasks:
                    try:
                        await task
                    except Exception as e:
                        task_errors.append(e)

                # Cancel the spinner task
                spinner_task.cancel()

                if len(task_errors):
                    raise ExceptionGroup(
                        f"Task failed on step {i + 1}",
                        task_errors,
                    )

                # Now merge the results with the params
                params |= results

        # Now perform the teardown
        for named_actions, anonymous_actions in reversed(actions_by_step):
            for action in named_actions.values():
                await action.cleanup()
            for action in anonymous_actions:
                await action.cleanup()


def show_current_params(params: Mapping[str, Any]):
    """
    Displays the current params to the user.
    """
    print()
    print("Running recipe with given parameters:")
    for param_name, param_value in params.items():
        print(f"  {param_name} = {param_value}")
    print()


def generate_actions_for_step(
    step: ActionStep,
    params: Mapping[str, Any],
) -> GeneratedActionStep:
    """
    Given a step, generate the actions
    """
    if isinstance(step, tuple):
        result: GeneratedActionStep = ({}, [])
        for step_item in step:
            # Use recursion so that we can simplify the handling of multiple
            # steps
            result = union_generated_action_step_items(
                result, generate_actions_for_step(step_item, params)
            )
        return result
    elif isinstance(step, MarkTenAction):
        # Single anonymous action
        return ({}, [step])
    elif isinstance(step, Mapping):
        # Collection of named actions
        return (dict(step), [])
    else:
        # step is an ActionGenerator function
        action_fn_output = execute_action_function(step, params)
        # Parse the result recursively
        return generate_actions_for_step(action_fn_output, params)


def union_generated_action_step_items(
    a: GeneratedActionStep,
    b: GeneratedActionStep,
) -> GeneratedActionStep:
    """
    Union a and b.
    """
    named_actions = a[0] | b[0]
    anonymous_actions = a[1] + b[1]
    return named_actions, anonymous_actions


def execute_action_function(
    fn: ActionGenerator,
    params: Mapping[str, Any],
) -> ActionStep:
    """
    Execute an action generator function, ensuring only the desired parameters
    are passed as kwargs.
    """
    args = inspect.getfullargspec(fn)
    kwargs_used = args[2] is not None
    if kwargs_used:
        return fn(**params)
    else:
        # Only pass the args used
        named_args = args[0]
        param_subset = {k: v for k, v in params.items() if k in named_args}
        return fn(**param_subset)
