"""Mujoco Robots for Experiments from https://github.com/kchua/handful-of-trials."""
from gym.envs.registration import register
try:
    import mujoco_py

    register(
        id='MBRLCartPole-v0',
        entry_point='rllib.environment.mujoco.cartpole:CartPoleEnv'
    )


    register(
        id='MBRLReacher3D-v0',
        entry_point='rllib.environment.mujoco.reacher:Reacher3DEnv'
    )


    register(
        id='MBRLPusher-v0',
        entry_point='rllib.environment.mujoco.pusher:PusherEnv'
    )


    register(
        id='MBRLHalfCheetah-v0',
        entry_point='rllib.environment.mujoco.half_cheetah:HalfCheetahEnv'
    )

except ImportError:
    pass