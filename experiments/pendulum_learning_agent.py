import math

import gpytorch
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.distributions import Uniform
import torch.optim as optim
from gpytorch.distributions import Delta
from tqdm import tqdm

from rllib.agent.mbmppo_agent import MBMPPOAgent
from rllib.algorithms.control.mppo import MBMPPO, train_mppo
from rllib.dataset.dataset import TrajectoryDataset
from rllib.dataset.datatypes import Observation
from rllib.dataset.transforms import MeanFunction, StateActionNormalizer, ActionClipper, \
    DeltaState
from rllib.dataset.utilities import stack_list_of_tuples, bootstrap_trajectory
from rllib.environment.system_environment import SystemEnvironment
from rllib.environment.systems import InvertedPendulum
from rllib.model.gp_model import ExactGPModel
from rllib.model.nn_model import NNModel
from rllib.model.pendulum_model import PendulumModel
from rllib.model.derived_model import TransformedModel, OptimisticModel, ExpectedModel
from rllib.model.ensemble_model import EnsembleModel
from rllib.policy import NNPolicy
from rllib.reward.pendulum_reward import PendulumReward
from rllib.util.collect_data import collect_model_transitions

from rllib.util.utilities import tensor_to_distribution
from rllib.util.plotting import plot_learning_losses, plot_values_and_policy
from rllib.util.rollout import rollout_model, rollout_policy, rollout_agent
from rllib.util.training import train_model
from rllib.util.neural_networks import DeterministicEnsemble
from rllib.util.neural_networks.utilities import freeze_parameters
from rllib.value_function import NNValueFunction

torch.manual_seed(0)
np.random.seed(0)


class StateTransform(nn.Module):
    extra_dim = 1

    def forward(self, states_):
        """Transform state before applying function approximation."""
        angle, angular_velocity = torch.split(states_, 1, dim=-1)
        states_ = torch.cat((torch.cos(angle), torch.sin(angle), angular_velocity),
                            dim=-1)
        return states_


def termination(state, action):
    return torch.any(state > 100) or torch.any(action > 100)


transformations = [
    ActionClipper(-1, 1),
    MeanFunction(DeltaState()),
    # StateActionNormalizer()
]

# %% Collect Data.
reward_model = PendulumReward()
environment = SystemEnvironment(InvertedPendulum(mass=0.3, length=0.5, friction=0.005,
                                                 step_size=1 / 80), reward=reward_model)

model = EnsembleModel(
    environment.dim_state, environment.dim_action, num_heads=5, layers=[64],
    biased_head=True, non_linearity='ReLU',
    input_transform=StateTransform(), deterministic=False)

dynamic_model = OptimisticModel(model, transformations)
model_optimizer = optim.Adam(dynamic_model.parameters(), lr=1e-4)

value_function = NNValueFunction(dim_state=environment.dim_state, layers=[64, 64],
                                 biased_head=False, input_transform=StateTransform())
policy = NNPolicy(dim_state=environment.dim_state, dim_action=environment.dim_action,
                  layers=[64, 64], biased_head=False, squashed_output=True,
                  input_transform=StateTransform(), deterministic=False)

mppo = MBMPPO(dynamic_model, reward_model, policy, value_function,
              epsilon=0.1, epsilon_mean=0.01, epsilon_var=0.00, gamma=0.99,
              num_action_samples=15,
              termination=termination)
mppo_optimizer = optim.Adam(
    [p for name, p in mppo.named_parameters() if 'model' not in name], lr=5e-4)

agent = MBMPPOAgent(dynamic_model, mppo, model_optimizer, mppo_optimizer,
                    transformations=transformations, max_len=int(1e5), batch_size=64,
                    num_env_rollouts=1, num_iter=30, num_mppo_iter=100,
                    num_simulation_steps=400, state_refresh_interval=2,
                    num_simulation_trajectories=8,
                    termination=termination,
                    gamma=0.99, exploration_episodes=3,
                    )
rollout_agent(environment, agent, num_episodes=25, max_steps=400)

# %% Test controller on Model.
test_state = torch.tensor(np.array([np.pi, 0.]), dtype=torch.get_default_dtype())

with torch.no_grad():
    trajectory = rollout_model(mppo.dynamical_model, mppo.reward_model,
                               lambda x: (policy(x)[0], torch.zeros(1)),
                               initial_state=test_state.unsqueeze(0),
                               max_steps=400)

    trajectory = Observation(*stack_list_of_tuples(trajectory))

states = trajectory.state[0]
rewards = trajectory.reward
fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(15, 5))

plt.sca(ax1)
plt.plot(states[:, 0], states[:, 1], 'x')
plt.plot(states[-1, 0], states[-1, 1], 'x')
plt.xlabel('Angle [rad]')
plt.ylabel('Angular velocity [rad/s]')

plt.sca(ax2)
plt.plot(rewards)
plt.xlabel('Time step')
plt.ylabel('Instantaneous reward')
plt.show()
print(f'Model Cumulative reward: {torch.sum(rewards):.2f}')

bounds = [(-2 * np.pi, 2 * np.pi), (-12, 12)]
ax_value, ax_policy = plot_values_and_policy(value_function, policy, bounds, [200, 200])
ax_value.plot(states[:, 0], states[:, 1], color='C1')
ax_value.plot(states[-1, 0], states[-1, 1], 'x', color='C1')
plt.show()

# %% Test controller on Environment.
environment = SystemEnvironment(InvertedPendulum(mass=0.3, length=0.5, friction=0.005,
                                                 step_size=1 / 80), reward=reward_model)
environment.state = test_state.numpy()
environment.initial_state = lambda: test_state.numpy()
trajectory = rollout_policy(environment, lambda x: (policy(x)[0], torch.zeros(1)),
                            max_steps=400, render=True)
trajectory = Observation(*stack_list_of_tuples(trajectory[0]))
print(f'Environment Cumulative reward: {torch.sum(trajectory.reward):.2f}')