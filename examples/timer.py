from markten import Recipe, actions, parameters


recipe = Recipe("timer")


recipe.parameter("duration", parameters.stdin("duration"))


def timer(duration: str):
    return actions.time.sleep(float(duration))


recipe.step("wait", timer)

recipe.run()
