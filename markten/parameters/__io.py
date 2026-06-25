import readline

import rich

from markten.more_itertools import RegenerateIterable, ReuseIterable

console = rich.get_console()


def stdin(param_name: str, repeat_values: bool = False):
    """
    Get parameter values as lines from stdin.
    """

    def generator():
        while True:
            try:
                value = console.input(f"Enter [cyan]{param_name}[/]: ")
                readline.add_history(value)
                yield value
            except EOFError:
                console.print()
                console.print(
                    f"Received EOF, no more values for [cyan]{param_name}[/]"
                )
                break

    if repeat_values:
        return ReuseIterable(generator())
    else:
        return RegenerateIterable(generator)
