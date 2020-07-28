from typing import Optional, Type, Union

import torch.nn as nn
from torch.distributions import Distribution
from torch.nn.modules.loss import _Loss
from torch.optim.optimizer import Optimizer

from rllib.algorithms.sac import MBSoftActorCritic
from rllib.dataset.datatypes import Termination
from rllib.model import AbstractModel
from rllib.policy import AbstractPolicy
from rllib.reward import AbstractReward
from rllib.util.parameter_decay import ParameterDecay
from rllib.value_function import AbstractValueFunction

from .model_based_agent import ModelBasedAgent

class MBSACAgent(ModelBasedAgent):
    """Implementation of Model-Based SAC Agent."""

    algorithm: MBSoftActorCritic
    def __init__(
        self,
        model_optimizer: Optional[Optimizer],
        policy: AbstractPolicy,
        value_function: AbstractValueFunction,
        dynamical_model: AbstractModel,
        reward_model: AbstractReward,
        optimizer: Optimizer,
        termination: Optional[Termination] = ...,
        initial_distribution: Optional[Distribution] = ...,
        plan_horizon: int = ...,
        plan_samples: int = ...,
        plan_elites: int = ...,
        max_memory: int = ...,
        model_learn_batch_size: int = ...,
        model_learn_num_iter: int = ...,
        bootstrap: bool = ...,
        sac_value_learning_criterion: Type[_Loss] = ...,
        sac_eta: Union[ParameterDecay, float] = ...,
        sac_regularization: bool = ...,
        sac_num_iter: int = ...,
        sac_gradient_steps: int = ...,
        sac_batch_size: Optional[int] = ...,
        sac_action_samples: int = ...,
        sac_target_num_steps: int = ...,
        sac_target_update_frequency: int = ...,
        sac_policy_update_frequency: int = ...,
        sim_num_steps: int = ...,
        sim_initial_states_num_trajectories: int = ...,
        sim_initial_dist_num_trajectories: int = ...,
        sim_memory_num_trajectories: int = ...,
        sim_refresh_interval: int = ...,
        sim_num_subsample: int = ...,
        sim_max_memory: int = ...,
        thompson_sampling: bool = ...,
        gamma: float = ...,
        exploration_steps: int = ...,
        exploration_episodes: int = ...,
        tensorboard: bool = ...,
        comment: str = ...,
    ) -> None: ...
