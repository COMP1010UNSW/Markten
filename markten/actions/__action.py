"""
# MarkTen / actions / action

Base class for MarkTen actions.
"""

from abc import abstractmethod
from typing import Any, Protocol, runtime_checkable

from markten.__spinners import SpinnerTask


@runtime_checkable
class MarkTenAction(Protocol):
    """
    An action object, which executes the given action.

    These objects are used by MarkTen to handle running a task, and performing
    any required cleanup afterwards.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the name to use for the action.
        """

    @abstractmethod
    async def run(self, task: SpinnerTask) -> Any:
        """
        Run the action.

        This should perform setup for the action. Its resultant awaitable
        should resolve once the setup is complete.

        It can also use the `task` object to display progress for the task and
        log any required output.

        The awaited result may be used as a parameter for future steps. For
        example, the `git.clone` action gives the path to the temporary
        directory cloned.
        """
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up after the recipe has been run, performing any required
        tear-down.

        The resultant awaitable should resolve once the tear-down is complete.
        """
        raise NotImplementedError
