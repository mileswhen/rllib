"""Implementation of DQNAgent Algorithms."""
from rllib.agent import QLearningAgent
from rllib.algorithms.q_learning import SoftQLearning
from rllib.policy import SoftMax
from rllib.value_function import AbstractQFunction
from rllib.dataset import ExperienceReplay
from rllib.util.parameter_decay import ParameterDecay
from torch.nn.modules.loss import _Loss
from torch.optim.optimizer import Optimizer
from typing import Union


class SoftQLearningAgent(QLearningAgent):
    q_learning: SoftQLearning
    policy: SoftMax

    def __init__(self, q_function: AbstractQFunction, criterion: _Loss,
                 optimizer: Optimizer, memory: ExperienceReplay,
                 temperature: Union[float, ParameterDecay], target_update_frequency: int = 4,
                 gamma: float = 1.0, exploration_steps: int = 0, exploration_episodes: int = 0) -> None: ...