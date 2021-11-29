"""Multi-objective Reduction classes."""
from typing import Any, Union
import torch.nn as nn
from abc import ABCMeta
from torch import LongTensor, Tensor

class AbstractMultiObjectiveReduction(nn.Module, metaclass=ABCMeta):
    dim: int
    def __init__(self, dim: int = ...) -> None: ...
    def __call__(self, value: Tensor) -> Tensor: ...

class GetIndexMultiObjectiveReduction(AbstractMultiObjectiveReduction):
    idx: LongTensor
    def __init__(
        self, idx: Union[int, LongTensor] = ..., *args: Any, **kwargs: Any
    ) -> None: ...

class WeightedMultiObjectiveReduction(AbstractMultiObjectiveReduction):
    weight: Tensor
    def __init__(self, weight: Tensor, *args: Any, **kwargs: Any) -> None: ...

class MeanMultiObjectiveReduction(AbstractMultiObjectiveReduction): ...
class SumMultiObjectiveReduction(AbstractMultiObjectiveReduction): ...
class MaxMultiObjectiveReduction(AbstractMultiObjectiveReduction): ...
class MinMultiObjectiveReduction(AbstractMultiObjectiveReduction): ...
class NoMultiObjectiveReduction(AbstractMultiObjectiveReduction): ...
