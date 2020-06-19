from typing import List, Optional, Tuple, Type, TypeVar

from numpy import ndarray
from torch import Tensor
from torch.utils import data

from rllib.dataset.datatypes import Observation
from rllib.dataset.transforms import AbstractTransform

T = TypeVar("T", bound="ExperienceReplay")

class ExperienceReplay(data.Dataset):
    max_len: int
    memory: ndarray
    weights: Tensor
    transformations: List[AbstractTransform]
    _ptr: int
    num_steps: int
    new_observation: bool
    def __init__(
        self,
        max_len: int,
        transformations: Optional[List[AbstractTransform]] = ...,
        num_steps: int = ...,
    ) -> None: ...
    @classmethod
    def from_other(cls: Type[T], other: T) -> T: ...
    def __len__(self) -> int: ...
    def __getitem__(self, item: int) -> Tuple[Observation, int, Tensor]: ...
    def _get_observation(self, idx: int) -> Observation: ...
    def reset(self) -> None: ...
    def append(self, observation: Observation) -> None: ...
    def get_batch(self, batch_size: int) -> Tuple[Observation, Tensor, Tensor]: ...
    @property
    def all_data(self) -> Observation: ...
    @property
    def is_full(self) -> bool: ...
    def update(self, indexes: Tensor, td_error: Tensor) -> None: ...
