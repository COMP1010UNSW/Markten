"""
# Markten / Recipe / Recipe

Overall recipe class
"""

import asyncio
import inspect
import os
import traceback
from collections.abc import Iterable, Mapping
from datetime import datetime, timedelta
from typing import Any, ParamSpec, TypeVar, overload

import humanize
import rich

from markten import __utils as utils
from markten.__consts import INTERRUPT_SPEED
from markten.__context import get_context
from markten.__recipe.parameters import ParameterManager
from markten.__recipe.runner import RecipeRunner
from markten.__recipe.step import RecipeStep, dict_to_actions
from markten.actions.__action import MarktenAction

P = ParamSpec("P")
T = TypeVar("T")


console = rich.get_console()


class Recipe:
    """
    Markten Recipe

    A recipe is the framework for building a Markten script. After creating
    the recipe, you can add parameters and steps to it, in order to specify
    how to execute the task.
    """

    def __init__(
        self,
        recipe_name: str,
        verbose: int | None = None,
    ) -> None:
        """
        Create a Markten Recipe

        A recipe is the framework for building a Markten script. After creating
        the recipe, you can add parameters and steps to it, in order to specify
        how to execute the task.

        Parameters
        ----------
        recipe_name : str
            Name of the recipe
        verbose : int
            Logging verbosity. Higher numbers will produce more-verbose output.
            Defaults to verbosity level set using CLI.
        """
        # Determine caller's module to show in debug info
        # https://stackoverflow.com/a/13699329/6335363
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        self.__file = module.__file__ if module is not None else None
        self.__name = recipe_name
        self.__params = ParameterManager()
        self.__steps: list[RecipeStep] = []
        self.__verbose = max(get_context().verbosity, verbose or 0)

    def parameter(self, name: str, values: Iterable[Any]) -> None:
        """Add a single parameter to the recipe.

        The parameter will be passed to all steps of the recipe.

        Parameters
        ----------
        name : str
            Name of the parameter
        values : Iterable[Any]
            An iterable of values for the parameter. The value will be lazily
            evaluated, so it is possible to perform actions such as reading
            from `stdin` for each value without overwhelming the user on script
            start-up.
        """
        self.__params.add(name, values)

    def parameters(self, parameters: Mapping[str, Iterable[Any]]) -> None:
        """Add a collection of parameters for the recipe.

        This should be a dictionary where each key is the name of a parameter,
        and each value is an iterable of values to use for that parameter.

        Parameters
        ----------
        parameters : dict[str, Iterable[Any]]
            Mapping of parameters.
        """
        for name, values in parameters.items():
            self.__params.add(name, values)

    @overload
    def step(
        self,
        action: MarktenAction | dict[str, MarktenAction],
        *actions: MarktenAction | dict[str, MarktenAction],
    ) -> None: ...

    @overload
    def step(self, action: MarktenAction[P, T]) -> MarktenAction[P, T]: ...

    def step(
        self,
        action: MarktenAction | dict[str, MarktenAction],
        *other_actions: MarktenAction | dict[str, MarktenAction],
    ) -> MarktenAction | None:
        """Add a step to the recipe.

        The step can be a variety of types:
        * A single `MarktenAction` function
        * A dictionary of `MarktenAction` functions. The yielded values of the
          actions will be stored as parameters for future steps using the name
          in the dictionary key.
        * Multiple of the above, as separate parameters

        If multiple actions are specified as one step, they will be run in
        parallel.

        Parameters
        ----------
        *step : MarktenAction | dict[str, MarktenAction]
            Action(s) to be run, as per the documentation above.
        """
        full_step: tuple[MarktenAction | dict[str, MarktenAction], ...] = (
            action,
            *other_actions,
        )

        actions: list[MarktenAction] = []
        for action in full_step:
            if isinstance(action, dict):
                # Convert dictionary into an action that produces that
                # dictionary
                actions.extend(dict_to_actions(action))
            else:
                actions.append(action)
        self.__steps.append(RecipeStep(len(self.__steps), actions))

        # If used as a decorator, return the function
        if len(full_step) == 1 and callable(full_step[0]):
            return full_step[0]
        else:
            return None

    def run(self):
        """Run the marking recipe for each permutation given by the generators.

        This begins the `asyncio` event loop, and so cannot be called from
        async code.
        """
        asyncio.run(self.async_run())

    async def async_run(self):
        """Run the marking recipe for each permutation given by the generators.

        This function can be used if an `asyncio` event loop is already active.
        """
        utils.recipe_banner(self.__name, self.__file)
        recipe_start = datetime.now()

        last_interrupt: datetime | None = None

        # For each permutation of parameters, run the recipe

        # Annoyingly, when an iterable throws an exception, its
        # iterator cannot be resumed. As such, this results in
        # immediate termination of the recipe, even if we were to manually
        # handle iteration using the `iter` and `next` functions, then handle
        # the exception within the loop. In the future, it could be possible to
        # instead handle when an iterator yields an object which
        # `isinstance(o, Exception)` like what is mentioned in
        # https://stackoverflow.com/a/27924011/6335363 's answers.
        # This would mean that the traceback information wouldn't be
        # available for debugging purposes though, so it is ***FAR***
        # from ideal.
        try:
            for permutation in self.__params:
                runner = RecipeRunner(permutation, self.__steps)
                try:
                    # The runner will gracefully handle its own errors.
                    await runner.run()
                except asyncio.CancelledError:
                    utils.print_exception(
                        "Interrupted while running recipe permutation.",
                        self.__verbose,
                    )
                    # If this is the second recipe to be interrupted in a short
                    # timespan, we should stop entirely.
                    if (
                        last_interrupt is not None
                        and datetime.now() - last_interrupt < INTERRUPT_SPEED
                    ):
                        print("Exiting due to repeated interruptions.")
                        break
                    else:
                        print("Interrupt repeatedly to quit.")
                        print()
                        last_interrupt = datetime.now()
        except KeyboardInterrupt:
            utils.print_exception(
                "Interrupted while evaluating recipe parameters.",
                self.__verbose,
            )
            return
        except Exception:
            utils.print_exception(
                "Error while evaluating recipe parameters:",
                self.__verbose,
            )
            return

        duration = datetime.now() - recipe_start
        iter_str = humanize.precisedelta(duration, minimum_unit="seconds")
        print()
        print(f"All permutations complete in {iter_str}")
