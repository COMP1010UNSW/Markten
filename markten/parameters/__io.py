def stdin(param_name: str):
    """
    Get parameter values as lines from stdin.
    """
    try:
        while True:
            value = input(f"Enter {param_name}: ")
            yield value
    except EOFError:
        pass
