"""
# MarkTen / __markten.py

Contains the definition for the main MarkTen class.
"""
import itertools
from .actions import MarkTenAction
from typing import Union, Callable, Any
from collections.abc import Sequence, Mapping, Iterable


GeneratorOption = Mapping[str, Iterable[Any]]


ActionFunction = Callable[
    ...,
    Union[
        MarkTenAction,
        tuple[MarkTenAction, ...],
        Mapping[str, MarkTenAction],
    ]
]
"""
An `ActionFunction` is a function that may accept parameters of previous
actions or of the generators, and returns a MarkTenAction, or a collection
thereof.

If the collection is in the form of a dictionary, the action's parameter will
be made available to following action functions, with the property name being
the same as the key in the dictionary.
"""


ActionGroup = Union[
    MarkTenAction,
    ActionFunction,
    tuple[ActionFunction | MarkTenAction, ...]
]
"""
An `ActionGroup` is a collection of `ActionFunction`s which should be executed
in sequence.
"""


class MarkTen:
    def __init__(
        self,
        generators: GeneratorOption | Sequence[GeneratorOption],
        actions: Sequence[ActionGroup],
    ) -> None:
        if isinstance(generators, Mapping):
            self.generators = generators
        else:
            self.generators = {}
            for generator in generators:
                self.generators |= generator
        self.actions = actions

    def run(self):
        # itertools.product
        # Need the equivalent for a dict of sequences
        ...
