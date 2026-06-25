"""
# Markten / Recipe / Runner

Runner for a single permutation of a recipe.
"""

from datetime import datetime
from typing import Any

import humanize
import rich

from markten import __utils as utils
from markten.__action_session import TeardownHook
from markten.__context import get_context
from markten.__recipe.hook import exec_hook
from markten.__recipe.step import RecipeStep

console = rich.get_console()


class RecipeRunner:
    def __init__(
        self,
        params: dict[str, Any],
        steps: list[RecipeStep],
    ) -> None:
        self.__params = params
        self.__steps = steps

    async def run(self):
        self.__show_current_params()
        start = datetime.now()

        try:
            await self.__do_run()
        except Exception:
            utils.print_exception(
                "Error while running this permutation of recipe",
                get_context().verbosity,
            )

        duration = datetime.now() - start
        perm_str = humanize.precisedelta(duration, minimum_unit="seconds")
        print(f"Permutation complete in {perm_str}")
        print()

    async def __do_run(self):
        """Actually run the recipe"""
        context: dict[str, Any] = {}
        teardown: list[list[TeardownHook]] = []

        try:
            for step in self.__steps:
                context, teardown_hooks = await step.run(
                    self.__params, context
                )
                teardown.append(teardown_hooks)
        finally:
            # Now do clean-up in reverse order
            for teardown_step in reversed(teardown):
                for teardown_hook in teardown_step:
                    await exec_hook(teardown_hook)

    def __show_current_params(self):
        """
        Displays the current params to the user.
        """
        print()
        print("Running recipe with given parameters:")
        for param_name, param_value in self.__params.items():
            print(f"  {param_name} = {param_value}")
        print()
