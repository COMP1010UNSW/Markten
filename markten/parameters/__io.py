from markten.more_itertools import RegenerateIterable, ReuseIterable


def stdin(param_name: str, repeat_values: bool = False):
    """
    Get parameter values as lines from stdin.
    """

    def generator():
        try:
            while True:
                yield input(f"Enter {param_name}: ")
        except (EOFError, KeyboardInterrupt):
            pass

    if repeat_values:
        return ReuseIterable(generator())
    else:
        return RegenerateIterable(generator)
