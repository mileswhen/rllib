"""Utilities for policies.."""


class SetDeterministic(object):
    """Context manager to make a policy deterministic temporarily.

    Parameters
    ----------
    policy: AbstractPolicy.
        policy to set deterministic.
    """

    def __init__(self, policy):
        self.policy = policy
        self.cache = self.policy.deterministic

    def __enter__(self):
        """Make the policy deterministic."""
        self.policy.deterministic = True

    def __exit__(self, *args):
        """Unfreeze the parameters."""
        self.policy.deterministic = self.cache
