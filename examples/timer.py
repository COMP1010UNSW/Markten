"""
Simple timer example
"""
from markten import ActionSession, Recipe, actions, parameters

recipe = Recipe("timer")


recipe.parameter("duration", map(float, parameters.stdin("duration")))


@recipe.step
def timer(action: ActionSession, duration: float):
    return actions.time.sleep(action, duration)

recipe.run()
