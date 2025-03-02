"""
Actions to do with Python
"""

import inspect
from collections.abc import Awaitable, Callable

from .__action import MarkTenAction


class function(MarkTenAction):
    """
    Action to run the given function.

    Note that the function will not be run in parallel, and so if it is
    long-running, this may cause the UI to freeze. As such, consider using
    `async_function` instead.
    """

    def __init__(self, fn: Callable[[], None]) -> None:
        """Create a `function` action.

        Parameters
        ----------
        fn : Callable[[], None]
            Function to execute.
        """
        self.__fn = fn

    def get_name(self) -> str:
        return str(inspect.signature(self.__fn))

    async def run(self, task) -> None:
        task.running()
        self.__fn()
        task.succeed()

    async def cleanup(self) -> None:
        pass


class async_function(MarkTenAction):
    """
    Action to run the given async function.
    """

    def __init__(self, fn: Callable[[], Awaitable[None]]) -> None:
        """Create an `async_function` action.

        Parameters
        ----------
        fn : Callable[[], Awaitable[None]]
            Async function to execute.
        """
        self.__fn = fn

    def get_name(self) -> str:
        return str(inspect.signature(self.__fn))

    async def run(self, task) -> None:
        task.running()
        await self.__fn()
        task.succeed()

    async def cleanup(self) -> None:
        pass
