

from collections.abc import Generator, Iterable, Mapping
from typing import Any


def recursive_generator(
    keys: list[str],
    params_dict: Mapping[str, Iterable[Any]],
) -> Generator[dict[str, Any], None, None]:
    """
    Recursively iterate over the given keys, producing a dict of values.
    """
    keys_head = keys[0]
    # Base case: this is the last remaining key
    if len(keys) == 1:
        for value in params_dict[keys_head]:
            yield {keys_head: value}
        return

    # Recursive case, other keys remain, and we need to iterate over those too
    keys_tail = keys[1:]

    for value in params_dict[keys_head]:
        # Iterate over remaining keys
        for current_params in recursive_generator(keys_tail, params_dict):
            # Overall keys is the union of the current key-value pair with
            # the params yielded by the recursion
            yield {keys_head: value} | current_params


def dict_permutations_iterator(
    params: Mapping[str, Iterable[Any]],
) -> Generator[dict[str, Any], None, None]:
    """
    Iterate over all possible parameter values provided by the generators.
    """
    return recursive_generator(list(params.keys()), params)
