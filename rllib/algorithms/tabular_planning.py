"""Implementation of algorithms for tabular planning.

The implemented algorithms are Policy Evaluation, Policy Iteration, Value Iteration.


References
----------
Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction.
MIT press.
Chapter 4.

"""
from rllib.value_function import TabularValueFunction
from rllib.policy import TabularPolicy
import torch
import numpy as np


__all__ = ['policy_evaluation', 'policy_iteration', 'value_iteration']


def _init_value_function(num_states, terminal_states: list = None):
    value_function = TabularValueFunction(num_states)
    for terminal_state in terminal_states:
        value_function.set_value(terminal_state, 0)

    return value_function


def policy_evaluation(policy, model, gamma, eps=1e-6, max_iter=1000,
                      value_function=None):
    """Implement of Policy Evaluation algorithm.

    Parameters
    ----------
    policy: AbstractPolicy
        policy to evaluate.
    model: AbstractModel
        a model of the environment. (also an MDP environment can be used).
    gamma: float
        discount factor.
    eps: float, optional
        desired precision, by default is 1e-6.
    max_iter: int, optional
        maximum number of iterations.
    value_function: TabularValueFunction, optional
        initial estimate of value function.

    Returns
    -------
    value_function: TabularValueFunction
        value function associated with the policy.


    References
    ----------
    Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction.
    MIT press.
    Chapter 4.1

    """
    if model.num_actions is None or model.num_states is None:
        raise NotImplementedError("Actions and States must be discrete and countable.")

    if value_function is None:
        value_function = _init_value_function(model.num_states, model.terminal_states)

    for _ in range(max_iter):
        error = 0
        for state in range(model.num_states):
            state = torch.tensor(state).long()

            value = value_function(state)
            value_ = 0
            policy_ = policy(state)
            for action in np.where(policy_.probs.detach().numpy())[0]:
                value_estimate = 0
                for next_state in np.where(model.kernel[state, action])[0]:
                    next_state = torch.tensor(next_state).long()
                    value_estimate += model.kernel[state, action, next_state] * (
                            model.reward[state, action]
                            + gamma * value_function(next_state)
                    )

                value_ += policy_.probs[action].item() * value_estimate

            error = max(error, torch.abs(value_ - value.item()))
            value_function.set_value(state, value_)
        if error < eps:
            break

    return value_function


def policy_iteration(model, gamma, eps=1e-6, max_iter=1000, value_function=None):
    """Implement Policy Iteration algorithm.

    Parameters
    ----------
    model: AbstractModel
        a model of the environment. (also an MDP environment can be used).
    gamma: float
        discount factor.
    eps: float, optional
        desired precision of policy evaluation step, by default is 1e-6.
    max_iter: int, optional
        maximum number of iterations.
    value_function: TabularValueFunction, optional
        initial estimate of value function.

    Returns
    -------
    policy: TabularPolicy.
        optimal policy.
    value_function: TabularValueFunction
        value function associated with the policy.


    References
    ----------
    Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction.
    MIT press.
    Chapter 4.3

    """
    if model.num_actions is None or model.num_states is None:
        raise NotImplementedError("Actions and States must be discrete and countable.")

    if value_function is None:
        value_function = _init_value_function(model.num_states, model.terminal_states)
    policy = TabularPolicy(num_states=model.num_states, num_actions=model.num_actions)

    for _ in range(max_iter):
        value_function = policy_evaluation(policy, model, gamma, eps,
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


def value_iteration(model, gamma, eps=1e-6, max_iter=1000, value_function=None):
    """Implement of Value Iteration algorithm.

    Parameters
    ----------
    model: AbstractModel
        a model of the environment. (also an MDP environment can be used).
    gamma: float
        discount factor.
    eps: float, optional
        desired precision, by default is 1e-6.
    max_iter: int, optional
        maximum number of iterations.
    value_function: TabularValueFunction, optional
        initial estimate of value function.

    Returns
    -------
    policy: TabularPolicy.
        optimal policy.
    value_function: TabularValueFunction
        value function associated with the policy.


    References
    ----------
    Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction.
    MIT press.
    Chapter 4.4

    """
    if model.num_actions is None or model.num_states is None:
        raise NotImplementedError("Actions and States must be discrete and countable.")

    if value_function is None:
        value_function = _init_value_function(model.num_states, model.terminal_states)
    policy = TabularPolicy(num_states=model.num_states, num_actions=model.num_actions)

    for _ in range(max_iter):
        error = 0
        for state in range(model.num_states):
            state = torch.tensor(state).long()

            value = value_function(state)

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

            value_, action = torch.max(value_, 0)
            error = max(error, torch.abs(value_ - value.item()))
            value_function.set_value(state, value_)
            policy.set_value(state, action)

        if error < eps:
            break

    return policy, value_function