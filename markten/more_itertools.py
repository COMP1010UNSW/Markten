from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Callable,
    Generator,
    Iterable,
    Iterator,
    Mapping,
)
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class AsyncReuseIterable(Generic[T]):
    """
    Iterable that runs the given iterable the first time it is iterated,
    and then uses the past results after that.
    """

    def __init__(self, iterable: AsyncIterable[T]) -> None:
        self.__iterable = iterable
        self.__past_values: list[T] = []
        self.__generated = False

    async def __aiter__(self) -> AsyncIterator[T]:
        async def first_iteration():
            self.__generated = True
            async for item in self.__iterable:
                self.__past_values.append(item)
                yield item

        async def later_iterations():
            for val in self.__past_values:
                yield val

        if self.__generated:
            return later_iterations()
        else:
            return first_iteration()


class ReuseIterable(Generic[T]):
    """
    Iterable that runs the given iterable the first time it is iterated,
    and then uses the past results after that.
    """

    def __init__(self, iterable: Iterable[T]) -> None:
        self.__iterable = iterable
        self.__past_values: list[T] = []
        self.__generated = False

    def __iter__(self) -> Iterator[T]:
        def first_iteration():
            self.__generated = True
            for item in self.__iterable:
                self.__past_values.append(item)
                yield item

        def later_iterations():
            yield from self.__past_values

        if self.__generated:
            return later_iterations()
        else:
            return first_iteration()


class AsyncRegenerateIterable(Generic[T]):
    """
    Iterable that reruns the given generator function each time it is iterated.
    """

    def __init__(self, generator: Callable[[], AsyncIterator[T]]) -> None:
        self.__generator = generator

    async def __aiter__(self) -> AsyncIterator[T]:
        return self.__generator()


class RegenerateIterable(Generic[T]):
    """
    Iterable that reruns the given generator function each time it is iterated.
    """

    def __init__(self, generator: Callable[[], Iterator[T]]) -> None:
        self.__generator = generator

    def __iter__(self) -> Iterator[T]:
        return self.__generator()


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
