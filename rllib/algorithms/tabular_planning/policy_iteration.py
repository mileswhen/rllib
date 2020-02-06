"""Policy iteration algorithm."""

from rllib.policy import TabularPolicy
import torch
import numpy as np
import torch.testing
from .utilities import init_value_function
from .policy_evaluation import iterative_policy_evaluation


def policy_iteration(model, gamma, eps=1e-6, max_iter=1000, value_function=None):
    """Implement Policy Iteration algorithm.

    Parameters
    ----------
    model:
    gamma: discount factor.
    eps: desired precision of policy evaluation step
    max_iter: maximum number of iterations
    value_function: initial estimate of value function, optional.

    Returns
    -------
    policy:
    value_function:


    References
    ----------
    Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction.
    MIT press.
    Chapter 4.3

    """
    if model.num_actions is None or model.num_states is None:
        raise NotImplementedError("Actions and States must be discrete and countable.")

    if value_function is None:
        value_function = init_value_function(model.num_states, model.terminal_states)
    policy = TabularPolicy(num_states=model.num_states, num_actions=model.num_actions)

    for _ in range(max_iter):
        value_function = iterative_policy_evaluation(policy, model, gamma, eps,
                                                     value_function=value_function)

        policy_stable = True
        for state in range(model.num_states):
            state = torch.tensor(state).long()
            old_action = policy(state).probs

            value_ = torch.zeros(model.num_actions)
            for action in range(model.num_actions):
                value_estimate = 0
                for next_state in np.where(model.kernel[state, action])[0]:
                    next_state = torch.tensor(next_state).long()
                    value_estimate += model.kernel[state, action, next_state] * (
                            model.reward[state, action]
                            + gamma * value_function(next_state)
                    )

                value_[action] = value_estimate

            action = torch.argmax(value_)
            policy.set_value(state, action)

            policy_stable &= (policy(state).probs == old_action).all().item()

        if policy_stable:
            break

    return policy, value_function
