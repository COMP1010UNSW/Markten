# MarkTen

Assess your students' work with all of the delight and none of the tedium.

## Installing

```bash
$ pip install markten
...
Successfully installed markten-0.1.0
```

Or to install in an independent environment, you can use `pipx`:

```bash
$ pipx install markten
  installed package markten 0.1.0, installed using Python 3.12.6
  These apps are now globally available
    - markten
done! ✨ 🌟 ✨
```

## How it works

Define your recipe parameters. For example, this recipe takes in git repo names
from stdin.

```py
from markten import Recipe, parameters, actions

marker = Recipe("Clone COMP1010 repos")

marker.parameter("repo", parameters.stdin("Repo name"))
```

Write simple marking recipes by defining simple functions for each step.

```py
# Functions can take arbitrary parameters
def setup(repo: str):
    """Set up marking environment"""
    # Clone the given git repo to a temporary directory
    directory = actions.git.clone(f"git@github.com:COMP1010UNSW/{repo}.git")
    return {
        "directory": directory,
    }

marker.step("Clone repo", setup)
```

The parameters returned by your previous steps can be used in later steps, just
by giving the function parameters the same name.

```py
def open_code(directory: Path):
    """Open the cloned git repo in VS Code"""
    return actions.editor.vs_code(directory)

marker.step("View in VS Code", open_code)
```

Then run the recipe. It'll run for every permutation of your parameters, making
it easy to mark in bulk.

```py
marker.run()
```

For more examples, see the examples directory.
