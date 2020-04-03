from abc import ABCMeta

import torch.nn as nn


class ParameterDecay(nn.Module, metaclass=ABCMeta):
    start: nn.Parameter
    end: nn.Parameter
    decay: nn.Parameter
    step: int

    def __init__(self, start: float, end: float = None, decay: float = None
                 ) -> None: ...

    def update(self) -> None: ...


class Constant(ParameterDecay): ...


class Learnable(ParameterDecay): ...

class ExponentialDecay(ParameterDecay): ...


class PolynomialDecay(ParameterDecay): ...


class LinearDecay(ParameterDecay): ...
