"""
Simple timer example
"""
from markten import Recipe, actions, parameters

recipe = Recipe("timer")


recipe.parameter("duration", map(float, parameters.stdin("duration")))


def timer(duration: float):
    return actions.time.sleep(duration)


recipe.step("wait", timer)

recipe.run()
