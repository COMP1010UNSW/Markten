from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

ActionResult = Any | dict[str, Any]
"""
Result from a Markten action.

Either a single value or a dict mapping from parameter names to their
corresponding values.

* Single values with no name will be discarded if used directly as a step.
* Dict values will be added to the `context` for future steps.
"""

ResultType = TypeVar("ResultType")

MarktenAction = Callable[..., Awaitable[ResultType]]
"""
A Markten action is an async generator function which optionally yields a state
to be used in future steps.

It is called, with the `anext` function being used to execute the action. Once
the function evaluates, it should yield a new state. Any required clean-up
should be written after this `yield`. The generator should only `yield` one
value. All other values will be ignored.
"""
