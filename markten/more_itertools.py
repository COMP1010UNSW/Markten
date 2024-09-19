from collections.abc import Iterable, Iterator
from typing import TypeVar, Generic, Callable


T = TypeVar('T')


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
            for item in self.__past_values:
                yield item

        if self.__generated:
            return later_iterations()
        else:
            return first_iteration()


class RegenerateIterable(Generic[T]):
    """
    Iterable that reruns the given generator function each time it is iterated.
    """

    def __init__(self, generator: Callable[[], Iterator[T]]) -> None:
        self.__generator = generator

    def __iter__(self) -> Iterator[T]:
        return self.__generator()
