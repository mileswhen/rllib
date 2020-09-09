"""ModelBasedAlgorithm."""
import torch

from rllib.dataset.utilities import stack_list_of_tuples
from rllib.util.training.utilities import sharpness

from .abstract_mb_algorithm import AbstractMBAlgorithm


def dyna_expand(
    base_algorithm,
    dynamical_model,
    reward_model,
    num_steps=1,
    num_samples=15,
    termination_model=None,
    *args,
    **kwargs,
):
    """Expand algorithm with dyna simulations."""
    #

    class Dyna(type(base_algorithm), AbstractMBAlgorithm):
        """Model Based Algorithm.

        A model based algorithm simulates trajectories with a model.
        """

        def __init__(self):
            super().__init__(
                **{**base_algorithm.__dict__, **dict(base_algorithm.named_modules())}
            )
            AbstractMBAlgorithm.__init__(
                self,
                dynamical_model,
                reward_model,
                num_steps=num_steps,
                num_samples=num_samples,
                termination_model=termination_model,
            )
            self.base_algorithm_name = base_algorithm.__class__.__name__

            self.policy.dist_params.update(**base_algorithm.policy.dist_params)
            self.policy_target.dist_params.update(
                **base_algorithm.policy_target.dist_params
            )

        def forward(self, observation, **kwargs_):
            """Rollout model and call base algorithm with transitions."""
            real_loss = super().forward(observation)
            with torch.no_grad():
                state = observation.state[..., 0, :]
                trajectory = self.simulate(state, self.policy)
            try:
                observation = stack_list_of_tuples(trajectory, dim=-2)
                sim_loss = super().forward(observation)
            except RuntimeError:
                sim_loss = super().forward(trajectory)

            sharpness_ = sharpness(self.dynamical_model, observation).item()
            alpha = 1.0 / (1.0 + self.num_steps * sharpness_)

            return (1 - alpha) * real_loss + alpha * sim_loss

    return Dyna()
