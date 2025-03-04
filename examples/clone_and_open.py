"""
Clone and open a bunch of students' work by reading student IDs from stdin.
"""

from argparse import ArgumentParser
from pathlib import Path

from markten import Recipe, actions, parameters

term = "25T1"


def command_line():
    """Set up parameters from command line"""
    parser = ArgumentParser("clone_and_open.py")
    parser.add_argument("lab", nargs="+")

    return parameters.from_object(parser.parse_args(), ["lab"])


def setup(lab: str, zid: str):
    """Set up lab exercise"""
    directory = actions.git.clone(
        f"git@nw-syd-gitlab.cseunsw.tech:COMP2511/{term}/students/{zid}/{
            lab
        }.git",
        branch="submission",
        fallback_to_main=True,
    )
    return {
        "directory": directory,
    }


def open_code(directory: Path):
    """Open directory in VS Code"""
    return actions.editor.vs_code(directory, remove_history=True)


def print_student_info(zid: str):
    """Look up student info"""
    return actions.process.run("ssh", "cse", "acc", zid)


marker = Recipe("COMP2511 Lab Marking")

marker.parameter("zid", parameters.stdin("zid"))
marker.parameters(command_line())

marker.step("setup repo", setup)
marker.step("view code", (open_code, print_student_info))

if __name__ == "__main__":
    marker.run()
