"""
# MarkTen / actions / action

Base class for MarkTen actions.
"""
from typing import Protocol, Any, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class MarkTenAction(Protocol):
    """
    An action object, which executes the given action
    """
    @abstractmethod
    async def run(self) -> Any:
        """
        Run the action.

        This should perform setup for the action. Its resultant awaitable
        should resolve once the setup is complete.

        The awaited result may be used as a parameter for future steps. For
        example, the `git.clone` action gives the path to the temporary
        directory cloned.
        """
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self) -> None:
        """
        Clean up after the recipe has been run, performing any required
        teardown.

        The resultant awaitable should resolve once the teardown is complete.
        """
        raise NotImplementedError
