"""
Simple example of opening a temporary directory in Zed
"""

from pathlib import Path

from markten import ActionSession, Recipe, actions, parameters

recipe = Recipe("timer")


recipe.parameter(
    "a", parameters.stdin("Press enter to continue or Ctrl+D to exit")
)


@recipe.step
async def mktemp(action: ActionSession):
    path = await actions.fs.temp_dir(action, remove=True)
    return {"mktemp": path}


@recipe.step
def open(action: ActionSession, mktemp: Path):
    return actions.editor.zed(action, mktemp)


recipe.run()
