"""Utilities for Half-Cheetah experiments."""

import numpy as np
import torch
import torch.distributions
import torch.nn as nn

from exps.gpucrl.util import large_state_termination, get_mpc_agent, get_mb_mppo_agent
from rllib.dataset.transforms import MeanFunction, ActionScaler, DeltaState
from rllib.environment import GymEnvironment
from rllib.reward.mujoco_rewards import HalfCheetahReward


class StateTransform(nn.Module):
    """Transform pendulum states to cos, sin, angular_velocity."""
    extra_dim = 1

    def forward(self, states):
        """Transform state before applying function approximation."""
        angles = states[..., 2:3]
        states_ = torch.cat(
            (states[..., :2], torch.cos(angles), torch.sin(angles), states[..., 3:]),
            dim=-1)
        return states_

    def inverse(self, states):
        """Inverse transformation of states."""
        cos, sin = states[..., 2:3], states[..., 3:4]
        angle = torch.atan2(sin, cos)
        states_ = torch.cat((states[..., :2], angle, states[..., 4:]), dim=-1)
        return states_


def get_agent_and_environment(params, agent_name):
    """Get experiment agent and environment."""
    torch.manual_seed(params.seed)
    np.random.seed(params.seed)

    # %% Define Environment.
    environment = GymEnvironment('MBRLHalfCheetah-v0', action_cost=params.action_cost,
                                 seed=params.seed)
    action_scale = environment.action_scale
    reward_model = HalfCheetahReward(action_cost=params.action_cost)

    # %% Define Helper modules
    transformations = [ActionScaler(scale=action_scale),
                       MeanFunction(DeltaState()),  # AngleWrapper(indexes=[1])
                       ]

    input_transform = None
    exploratory_distribution = torch.distributions.MultivariateNormal(
        torch.zeros(environment.dim_state), torch.eye(environment.dim_state)
    )

    if agent_name == 'mpc':
        agent = get_mpc_agent(environment.name, environment.dim_state,
                              environment.dim_action,
                              params, reward_model,
                              action_scale=action_scale,
                              transformations=transformations,
                              input_transform=input_transform,
                              termination=large_state_termination,
                              initial_distribution=exploratory_distribution)
    elif agent_name == 'mbmppo':
        agent = get_mb_mppo_agent(
            environment.name, environment.dim_state, environment.dim_action,
            params, reward_model, input_transform=input_transform,
            action_scale=action_scale,
            transformations=transformations,
            termination=large_state_termination,
            initial_distribution=exploratory_distribution)
    else:
        raise NotImplementedError

    return environment, agent