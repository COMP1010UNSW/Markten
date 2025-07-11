"""
# Markten / Recipe / Runner

Runner for a single permutation of a recipe.
"""

from datetime import datetime
from typing import Any

import humanize

from markten.__recipe.step import RecipeStep, run_to_completion
from markten.actions.__action import ActionGenerator


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
        except Exception as e:
            # TODO: Better error handling (pretty-print exceptions)
            print("Error while running this permutation of recipe")
            print(e)


        duration = datetime.now() - start
        perm_str = humanize.precisedelta(duration, minimum_unit="seconds")
        print(f"Permutation complete in {perm_str}")

    async def __do_run(self):
        """Actually run the recipe"""
        context: dict[str, Any] = {}
        step_generators: list[ActionGenerator] = []

        for step in self.__steps:
            gen = step.run(self.__params, context)
            context = await anext(gen)
            step_generators.append(gen)

        # Now do clean-up in reverse order
        for gen in reversed(step_generators):
            # Run to completion to do clean-up
            await run_to_completion(gen)


    def __show_current_params(self):
        """
        Displays the current params to the user.
        """
        print()
        print("Running recipe with given parameters:")
        for param_name, param_value in self.__params.items():
            print(f"  {param_name} = {param_value}")
        print()
