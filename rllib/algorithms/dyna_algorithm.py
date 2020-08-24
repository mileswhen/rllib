"""ModelBasedAlgorithm."""
import torch

from rllib.dataset.utilities import stack_list_of_tuples
from rllib.util.neural_networks.utilities import repeat_along_dimension
from rllib.util.rollout import rollout_model
from rllib.value_function.integrate_q_value_function import IntegrateQValueFunction

from .abstract_algorithm import AbstractAlgorithm


class DynaAlgorithm(AbstractAlgorithm):
    """Model Based Algorithm.

    A model based algorithm simulates trajectories with a model.
    """

    def __init__(
        self,
        base_algorithm,
        dynamical_model,
        reward_model,
        num_steps=1,
        num_samples=15,
        termination=None,
        *args,
        **kwargs,
    ):
        if "gamma" not in kwargs:
            kwargs["gamma"] = base_algorithm.gamma
        super().__init__(
            critic=base_algorithm.critic,
            policy=base_algorithm.policy,
            criterion=base_algorithm.criterion,
            reward_transformer=base_algorithm.reward_transformer,
            *args,
            **kwargs,
        )
        self.base_algorithm = base_algorithm

        self.dynamical_model = dynamical_model
        self.reward_model = reward_model
        self.num_steps = num_steps
        self.num_samples = num_samples
        self.termination = termination

        if hasattr(self.base_algorithm, "value_function"):
            self.value_function = self.base_algorithm.value_function
        elif hasattr(self.base_algorithm, "q_target"):
            self.value_function = IntegrateQValueFunction(
                self.base_algorithm.q_target, self.base_algorithm.policy, 1
            )
        else:
            self.value_function = None

    def simulate(self, state):
        """Simulate trajectories starting from a state."""
        state = repeat_along_dimension(state, number=self.num_samples, dim=0)
        state = state.reshape(-1, *self.dynamical_model.dim_state)
        return rollout_model(
            self.dynamical_model,
            self.reward_model,
            self.policy,
            state,
            max_steps=self.num_steps,
            termination=self.termination,
        )

    def forward(self, observation):
        """Rollout model and call base algorithm with transitions."""
        with torch.no_grad():
            trajectory = self.simulate(observation.state)
            observation = stack_list_of_tuples(trajectory, dim=-2)
        try:
            return self.base_algorithm(observation)
        except RuntimeError:
            return self.base_algorithm(trajectory)

    @torch.jit.export
    def update(self):
        """Update algorithm parameters."""
        self.base_algorithm.update()

    @torch.jit.export
    def reset(self):
        """Reset algorithms parameters."""
        self.base_algorithm.reset()

    def info(self):
        """Return info parameters for logging."""
        return self.base_algorithm.info()

    def reset_info(self, *args, **kwargs):
        """Call reset info in base algorithm."""
        self.base_algorithm.reset_info(*args, **kwargs)
