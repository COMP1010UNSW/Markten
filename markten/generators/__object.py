from collections.abc import Sequence
from typing import Any


def from_object(
    obj: object,
    param_names: Sequence[str],
) -> dict[str, Sequence[Any]]:
    """
    Get params from an object.

    This can be used with argparse results.
    """
    params = {}

    for name in param_names:
        value = getattr(obj, name)
        if isinstance(value, Sequence):
            params[name] = value
        else:
            params[name] = [value]

    return params
