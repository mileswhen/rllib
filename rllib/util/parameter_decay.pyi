from abc import ABCMeta

import torch.nn as nn

class ParameterDecay(nn.Module, metaclass=ABCMeta):
    start: nn.Parameter
    end: nn.Parameter
    decay: nn.Parameter
    step: int
    def __init__(
        self, start: float, end: float = None, decay: float = None
    ) -> None: ...
    def update(self) -> None: ...

class Constant(ParameterDecay): ...

class Learnable(ParameterDecay):
    positive: bool
    def __init__(self, start: float, positive: bool = True) -> None: ...

class ExponentialDecay(ParameterDecay): ...
class PolynomialDecay(ParameterDecay): ...
class LinearDecay(ParameterDecay): ...
class LinearGrowth(ParameterDecay): ...
