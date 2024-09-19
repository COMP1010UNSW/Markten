"""
Actions to do with Python
"""
import inspect
from .__action import MarkTenAction
from typing import Callable, Awaitable


class function(MarkTenAction):
    """
    Run the given function
    """
    def __init__(self, fn: Callable[[], None]) -> None:
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
    Run the given function
    """
    def __init__(self, fn: Callable[[], Awaitable[None]]) -> None:
        self.__fn = fn

    def get_name(self) -> str:
        return str(inspect.signature(self.__fn))

    async def run(self, task) -> None:
        task.running()
        await self.__fn()
        task.succeed()

    async def cleanup(self) -> None:
        pass
