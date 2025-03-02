"""
# Examples / Multicat

Just display the user's text back to them.

Demonstrates the difference between `repeat_values` flags for the `stdin`
parameter generator.
"""

from markten import Recipe, actions, parameters

recipe = Recipe("cat")

recipe.parameter("line1", parameters.stdin("line1", repeat_values=False))
recipe.parameter("line2", parameters.stdin("line2", repeat_values=True))


def cat(line1, line2):
    return actions.python.function(lambda: print(line1, line2))


recipe.step("display", cat)

recipe.run()
