from .abstract_agent import AbstractAgent
from rllib.dataset import TrajectoryDataset
from rllib.policy import RandomPolicy
import torch


class RandomAgent(AbstractAgent):
    def __init__(self, dim_state, dim_action, num_action=None, scale=1.0):
        super().__init__()
        self._policy = RandomPolicy(dim_state, dim_action, num_action=num_action,
                                    scale=scale)
        self._trajectory = []
        self._dataset = TrajectoryDataset(sequence_length=1)

    def __str__(self):
        return "Random Agent"

    def act(self, state):
        state = torch.from_numpy(state).float()
        action = self._policy.action(state).sample()
        return action.detach().numpy()

    def observe(self, observation):
        super().observe(observation)
        self._trajectory.append(observation)

    def start_episode(self):
        super().start_episode()
        self._trajectory = []

    def end_episode(self):
        self._dataset.append(self._trajectory)
