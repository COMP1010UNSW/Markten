"""
# Markten / Recipe / Recipe

Overall recipe class
"""

import asyncio
import inspect
import traceback
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

import humanize
from rich import print

from markten import __utils as utils
from markten.__recipe.parameters import ParameterManager
from markten.__recipe.runner import RecipeRunner
from markten.__recipe.step import RecipeStep, dict_to_actions
from markten.actions.__action import MarktenAction


class Recipe:
    def __init__(
        self,
        recipe_name: str,
        verbose: int = 0,
    ) -> None:
        """
        Create a MarkTen Recipe

        A recipe is the framework for building a MarkTen script. After creating
        the recipe, you can add parameters and steps to it, in order to specify
        how to execute the task.

        Parameters
        ----------
        recipe_name : str
            Name of the recipe
        verbose : int
            Logging verbosity. Higher numbers will produce more-verbose output.
        """
        # Determine caller's module to show in debug info
        # https://stackoverflow.com/a/13699329/6335363
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        self.__file = module.__file__ if module is not None else None
        self.__name = recipe_name
        self.__params = ParameterManager()
        self.__steps: list[RecipeStep] = []
        self.__verbose = verbose

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

    def step(
        self,
        *step: MarktenAction | dict[str, MarktenAction],
    ) -> None:
        """Add a step to the recipe.

        The step can be a variety of types:
        * A single `MarkTenAction` function
        * A dictionary of `MarkTenAction` functions. The yielded values of the
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
        actions: list[MarktenAction] = []
        for action in step:
            if isinstance(action, dict):
                # Convert dictionary into an action that produces that
                # dictionary
                actions.extend(dict_to_actions(action))
            else:
                actions.append(action)
        self.__steps.append(RecipeStep(len(self.__steps), actions))

    def run(self):
        """Run the marking recipe for each permutation given by the generators.

        This begins the `asyncio` event loop, and so cannot be called from
        async code.
        """
        try:
            asyncio.run(self.async_run())
        except KeyboardInterrupt as e:
            print()
            print("[bold red]Interrupted[/]")
            if self.__verbose >= 1:
                traceback.print_exception(e)
            else:
                print(
                    "To show stack trace, set recipe verbosity to a value >= 1"
                )
            print("Goodbye!")

    async def async_run(self):
        """Run the marking recipe for each permutation given by the generators.

        This function can be used if an `asyncio` event loop is already active.
        """
        utils.recipe_banner(self.__name, self.__file)
        recipe_start = datetime.now()

        # For each permutation of parameters, run the recipe
        for permutation in self.__params:
            runner = RecipeRunner(permutation, self.__steps)
            await runner.run()

        duration = datetime.now() - recipe_start
        iter_str = humanize.precisedelta(duration, minimum_unit="seconds")
        print()
        print(f"All permutations complete in {iter_str}")
