"""
# MarkTen / Main

Programmatic entrypoint to MarkTen, allowing it to be run as a script.
"""
import sys
import os
from . import __utils as utils


def show_info():
    utils.show_banner()
    print("Usage:")
    print("  markten <recipe-script> [arguments]")
    print("  This will execute the given script in Markten's Python")
    print("  environment.")
    print("License: MIT")
    print("Author: Maddy Guthridge")


def main():
    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help"]:
        show_info()
        exit(1)
    else:
        # Attempt to execute the given file with any remaining arguments
        recipe = sys.argv[1]
        args = sys.argv[2:]

        os.execv(sys.executable, ("python", recipe, *args))


if __name__ == '__main__':
    main()
