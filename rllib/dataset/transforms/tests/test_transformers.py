from rllib.dataset.transforms import *
from rllib.dataset.datatypes import Observation
from rllib.dataset.utilities import stack_list_of_tuples
import pytest
import torch
import torch.testing


def get_observation(reward=None):
    return Observation(state=torch.randn(4),
                       action=torch.randn(4),
                       reward=reward if reward else torch.randn(1),
                       next_state=torch.randn(4),
                       done=False).to_torch()


@pytest.fixture
def trajectory():
    t = []
    for reward in [3., -2., 0.5]:
        t.append(get_observation(reward))
    return t


class MeanModel(torch.nn.Module):
    def forward(self, state, action):
        return 2 * state + action


class TestMeanFunction(object):
    def test_call(self, trajectory):
        transformer = MeanFunction(MeanModel())
        for observation in trajectory:
            transformed_observation = transformer(observation)
            torch.testing.assert_allclose(transformed_observation.state,
                                            observation.state)
            torch.testing.assert_allclose(transformed_observation.action,
                                            observation.action)
            torch.testing.assert_allclose(transformed_observation.reward,
                                            observation.reward)
            assert transformed_observation.done == observation.done

            mean = 2 * observation.state + observation.action
            torch.testing.assert_allclose(transformed_observation.next_state,
                                            observation.next_state - mean)

        transformer.update(trajectory)

    def test_inverse(self, trajectory):
        transformer = MeanFunction(MeanModel())
        for observation in trajectory:
            inverse_observation = transformer.inverse(transformer(observation))
            assert observation == inverse_observation
            assert observation is not inverse_observation


class TestRewardClipper(object):
    @pytest.fixture(params=[0., None], scope="class")
    def minimum(self, request):
        return request.param

    @pytest.fixture(params=[1., None], scope="class")
    def maximum(self, request):
        return request.param

    def test_call(self, trajectory):
        transformer = RewardClipper(min_reward=0., max_reward=1.)
        for observation in trajectory:
            transformed_observation = transformer(observation)
            assert transformed_observation.reward >= 0.
            assert transformed_observation.reward <= 1.
            torch.testing.assert_allclose(transformed_observation.state,
                                            observation.state)
            torch.testing.assert_allclose(transformed_observation.action,
                                            observation.action)
            torch.testing.assert_allclose(transformed_observation.next_state,
                                            observation.next_state)
            assert transformed_observation.done == observation.done

            if 0 <= observation.reward <= 1:
                assert transformed_observation.reward == observation.reward
            elif observation.reward <= 0:
                assert transformed_observation.reward == 0.
            elif observation.reward >= 1.:
                assert transformed_observation.reward == 1.

    def test_inverse(self, trajectory):
        transformer = RewardClipper(min_reward=0., max_reward=1.)
        for observation in trajectory:
            transformed_observation = transformer(observation)
            inverse_observation = transformer.inverse(transformed_observation)

            torch.testing.assert_allclose(transformed_observation.state,
                                            observation.state)
            torch.testing.assert_allclose(transformed_observation.action,
                                            observation.action)
            torch.testing.assert_allclose(transformed_observation.next_state,
                                            observation.next_state)
            assert transformed_observation.done == observation.done
            torch.testing.assert_allclose(inverse_observation.reward,
                                            transformed_observation.reward)


class TestActionNormalize(object):
    @pytest.fixture(params=[True, False], scope="class")
    def preserve_origin(self, request):
        return request.param

    def test_update(self, trajectory, preserve_origin):
        transformer = ActionNormalizer(preserve_origin)

        trajectory = stack_list_of_tuples(trajectory)

        mean = torch.mean(trajectory.action, 0)
        var = torch.var(trajectory.action, 0)

        transformer.update(trajectory)
        torch.testing.assert_allclose(transformer._normalizer._mean, mean)
        torch.testing.assert_allclose(transformer._normalizer._variance, var)

    def test_call(self, trajectory, preserve_origin):
        transformer = ActionNormalizer(preserve_origin)

        trajectory = stack_list_of_tuples(trajectory)
        transformer.update(trajectory)
        observation = get_observation()
        transformed = transformer(observation)

        if preserve_origin:
            mean = 0
            scale = torch.sqrt(transformer._normalizer._variance
                               + transformer._normalizer._mean ** 2)
        else:
            mean = transformer._normalizer._mean
            scale = torch.sqrt(transformer._normalizer._variance)
        torch.testing.assert_allclose(transformed.action,
                                      (observation.action - mean) / scale)

        torch.testing.assert_allclose(transformed.state, observation.state)
        torch.testing.assert_allclose(transformed.reward, observation.reward)
        torch.testing.assert_allclose(transformed.next_state, observation.next_state)
        assert transformed.done == observation.done

    def test_inverse(self, trajectory, preserve_origin):

        transformer = ActionNormalizer(preserve_origin)
        trajectory = stack_list_of_tuples(trajectory)
        transformer.update(trajectory)

        observation = get_observation()
        inverse_observation = transformer.inverse(transformer(observation))
        assert observation == inverse_observation
        assert observation is not inverse_observation


class TestStateNormalize(object):
    @pytest.fixture(params=[True, False], scope="class")
    def preserve_origin(self, request):
        return request.param

    def test_update(self, trajectory, preserve_origin):
        transformer = StateNormalizer(preserve_origin)

        trajectory = stack_list_of_tuples(trajectory)

        mean = torch.mean(trajectory.state, 0)
        var = torch.var(trajectory.state, 0)

        transformer.update(trajectory)
        torch.testing.assert_allclose(transformer._normalizer._mean, mean)
        torch.testing.assert_allclose(transformer._normalizer._variance, var)

    def test_call(self, trajectory, preserve_origin):
        transformer = StateNormalizer(preserve_origin)
        trajectory = stack_list_of_tuples(trajectory)

        transformer.update(trajectory)
        observation = get_observation()
        transformed = transformer(observation)

        if preserve_origin:
            mean = 0
            scale = torch.sqrt(transformer._normalizer._variance
                                 + transformer._normalizer._mean ** 2)
        else:
            mean = transformer._normalizer._mean
            scale = torch.sqrt(transformer._normalizer._variance)
        torch.testing.assert_allclose(transformed.state,
                                        (observation.state - mean) / scale)
        torch.testing.assert_allclose(transformed.next_state,
                                        (observation.next_state - mean) / scale)

        torch.testing.assert_allclose(transformed.action, observation.action)
        torch.testing.assert_allclose(transformed.reward, observation.reward)
        assert transformed.done == observation.done

    def test_inverse(self, trajectory, preserve_origin):
        transformer = StateNormalizer(preserve_origin)

        trajectory = stack_list_of_tuples(trajectory)

        transformer.update(trajectory)

        observation = get_observation()
        inverse_observation = transformer.inverse(transformer(observation))
        assert observation == inverse_observation
        assert observation is not inverse_observation
