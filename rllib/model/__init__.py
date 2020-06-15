"""Dynamical model module.

A model is a mapping from states and actions to next_state distributions.

It should will accept raw states and actions and, if needed, perform any transformation
inside the model.

The derived models provide such functionality.
"""
from .abstract_model import AbstractModel
from .derived_model import ExpectedModel, OptimisticModel, TransformedModel
from .ensemble_model import EnsembleModel
from .gp_model import ExactGPModel, RandomFeatureGPModel, SparseGPModel
from .linear_model import LinearModel
from .nn_model import NNModel
