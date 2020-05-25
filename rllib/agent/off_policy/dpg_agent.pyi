from torch.nn.modules.loss import _Loss
from torch.optim.optimizer import Optimizer

from rllib.algorithms.dpg import DPG
from rllib.dataset import ExperienceReplay
from rllib.exploration_strategies import AbstractExplorationStrategy
from rllib.policy import AbstractPolicy
from rllib.value_function import AbstractQFunction
from .off_policy_agent import OffPolicyAgent


class DPGAgent(OffPolicyAgent):
    exploration: AbstractExplorationStrategy
    algorithm: DPG

    def __init__(self,env_name: str, q_function: AbstractQFunction, policy: AbstractPolicy,
                 exploration: AbstractExplorationStrategy, criterion: _Loss,
                 optimizer: Optimizer,
                 memory: ExperienceReplay, num_iter: int = 1, batch_size: int = 64,
                 target_update_frequency: int = 4,
                 policy_noise: float = 0., noise_clip: float = 1.,
                 train_frequency: int = 0, num_rollouts: int = 1, gamma: float = 1.0,
                 exploration_steps: int = 0, exploration_episodes: int = 0,
                 comment: str = '') -> None: ...