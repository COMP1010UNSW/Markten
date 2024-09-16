def stdin(param_name: str):
    """
    Get generators as lines from stdin.
    """
    try:
        value = input(f"Enter {param_name}: ")
        yield value
    except EOFError:
        pass
