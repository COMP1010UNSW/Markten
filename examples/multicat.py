"""
# Examples / Multicat

Just display the user's text back to them.

Demonstrates the difference between `repeat_values` flags for the `stdin`
parameter generator.
"""

from markten import Recipe, parameters

recipe = Recipe("cat")

recipe.parameter(
    "no_repeat", parameters.stdin("no_repeat value", repeat_values=False)
)
recipe.parameter(
    "repeat", parameters.stdin("repeat value", repeat_values=True)
)


async def cat(no_repeat, repeat):
    print("no_repeat:", no_repeat)
    print("repeat:", repeat)


recipe.step(cat)

recipe.run()
