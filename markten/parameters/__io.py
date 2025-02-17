import readline

from markten.more_itertools import RegenerateIterable, ReuseIterable


def stdin(param_name: str, repeat_values: bool = False):
    """
    Get parameter values as lines from stdin.
    """

    def generator():
        try:
            while True:
                value = input(f"Enter {param_name}: ")
                readline.add_history(value)
                yield value
        except (EOFError, KeyboardInterrupt):
            pass

    if repeat_values:
        return ReuseIterable(generator())
    else:
        return RegenerateIterable(generator)
