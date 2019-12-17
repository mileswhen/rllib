import pytest
from rllib.agent import DQNAgent, QLearningAgent, GQLearningAgent, DDQNAgent
from rllib.util import rollout_agent
from rllib.value_function import NNQFunction, TabularQFunction
from rllib.dataset import ExperienceReplay
from rllib.exploration_strategies import EpsGreedy
from rllib.environment import GymEnvironment, EasyGridWorld
import torch.nn.functional as func
import torch.optim

NUM_EPISODES = 25
MAX_STEPS = 25
TARGET_UPDATE_FREQUENCY = 4
TARGET_UPDATE_TAU = 0.9
MEMORY_MAX_SIZE = 5000
BATCH_SIZE = 64
LEARNING_RATE = 0.001
GAMMA = 0.99
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 500
LAYERS = [64, 64]
SEED = 0


@pytest.fixture(params=['CartPole-v0', 'NChain-v0'])
def environment(request):
    return request.param


@pytest.fixture(params=[DQNAgent, QLearningAgent, GQLearningAgent, DDQNAgent])
def agent(request):
    return request.param


def test_nnq_interaction(environment, agent):
    environment = GymEnvironment(environment, SEED, MAX_STEPS)
    exploration = EpsGreedy(EPS_START, EPS_END, EPS_DECAY)
    q_function = NNQFunction(environment.dim_observation, environment.dim_action,
                             num_states=environment.num_states,
                             num_actions=environment.num_actions,
                             layers=LAYERS,
                             tau=TARGET_UPDATE_TAU
                             )

    optimizer = torch.optim.Adam
    criterion = func.mse_loss
    memory = ExperienceReplay(max_len=MEMORY_MAX_SIZE, batch_size=BATCH_SIZE)

    hyper_params = {
        'target_update_frequency': TARGET_UPDATE_FREQUENCY,
        'learning_rate': LEARNING_RATE
    }
    q_agent = agent(q_function=q_function, exploration=exploration,
                    criterion=criterion, optimizer=optimizer, memory=memory,
                    hyper_params=hyper_params, gamma=GAMMA)
    rollout_agent(environment, q_agent, num_episodes=NUM_EPISODES)


def test_tabular_interaction(agent):
    LEARNING_RATE = 0.1
    environment = EasyGridWorld()
    exploration = EpsGreedy(EPS_START, EPS_END, EPS_DECAY)
    q_function = TabularQFunction(num_states=environment.num_states,
                                  num_actions=environment.num_actions)

    optimizer = torch.optim.Adam
    criterion = func.mse_loss
    memory = ExperienceReplay(max_len=MEMORY_MAX_SIZE)

    hyper_params = {
        'target_update_frequency': TARGET_UPDATE_FREQUENCY,
        'batch_size': BATCH_SIZE,
        'learning_rate': LEARNING_RATE
    }
    q_agent = agent(q_function=q_function, exploration=exploration,
                    criterion=criterion, optimizer=optimizer, memory=memory,
                    hyper_params=hyper_params, gamma=GAMMA, episode_length=10)

    rollout_agent(environment, q_agent, num_episodes=NUM_EPISODES)
    print(q_function.table)