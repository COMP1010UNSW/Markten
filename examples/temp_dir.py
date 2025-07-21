"""
Simple timer example
"""
from markten import ActionSession, Recipe, actions, parameters

recipe = Recipe("timer")


recipe.parameter("a", parameters.stdin("Press enter to continue"))


@recipe.step
def mktemp(action: ActionSession):
    return actions.fs.temp_dir(action, remove=True)


recipe.run()
