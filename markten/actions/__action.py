"""
# MarkTen / actions / action

Base class for MarkTen actions.
"""
from typing import Protocol, Any
from abc import abstractmethod


class MarkTenAction(Protocol):
    """
    An action object, which executes the given action
    """
    @abstractmethod
    async def begin(self) -> None:
        """
        Begin the action.

        This should perform setup for the action. Its resultant awaitable
        should resolve once the setup is complete.
        """
        raise NotImplementedError

    async def get_parameter(self) -> Any:
        """
        Returns the parameter produced by the action, which may be used by
        future actions.

        For example the `git.clone` action produces a `Path` to the temporary
        directory in which the repo was cloned.

        Returns:
            Any: resultant parameter.
        """
        return None

    @abstractmethod
    async def end(self) -> None:
        """
        Finish the action, performing any required teardown.

        The resultant awaitable should resolve once the teardown is complete.
        """
        raise NotImplementedError
