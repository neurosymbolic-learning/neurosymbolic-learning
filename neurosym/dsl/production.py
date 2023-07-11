from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict

from ..types.type_signature import TypeSignature


class Production(ABC):
    """
    Represents a production rule in a simple s-expression grammar.

    Has a symbol, a type signature, and a function that represents the function represented.
    """

    @abstractmethod
    def symbol(self):
        pass

    @abstractmethod
    def type_signature(self) -> TypeSignature:
        """
        Return a TypeSignature object representing the type signature of this production.
        """

    @abstractmethod
    def initialize(self) -> object:
        """
        Return some state that this production might need to compute its function.
            E.g., for a neural network production, this might be the weights of the network.
        """

    @abstractmethod
    def compute_on_pytorch(self, state, *inputs):
        """
        Return the resulting pytorch expression of computing this function on the inputs.
            Takes in the state of the production, which is the result of initialize().

        Effectively a form of denotation semantics.
        """


@dataclass
class ConcreteProduction(Production):
    _symbol: str
    _type_signature: TypeSignature
    _compute_on_pytorch: Callable[..., object]

    def symbol(self):
        return self._symbol

    def type_signature(self) -> TypeSignature:
        return self._type_signature

    def initialize(self) -> object:
        return {}

    def compute_on_pytorch(self, state, *inputs):
        assert state == {}
        return self._compute_on_pytorch(*inputs)


@dataclass
class ParameterizedProduction(ConcreteProduction):
    _initialize: Callable[[], Dict[str, object]]

    def initialize(self) -> object:
        return self._initialize()

    def compute_on_pytorch(self, state, *inputs):
        return self._compute_on_pytorch(*inputs, **state)
