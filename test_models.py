import numpy as np

from stable_baselines import deepq
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines.common import set_global_seeds

from slay_the_script.env import SlayTheScriptEnv

LEARN_FUNC_DICT = {
    'a2c': lambda e: A2C(policy="MlpPolicy", learning_rate=1e-3, n_steps=1,
                         gamma=0.7, env=e).learn(total_timesteps=10000, seed=0),
    'acer': lambda e: ACER(policy="MlpPolicy", env=e,
                           n_steps=1, replay_ratio=1).learn(total_timesteps=15000, seed=0),
    'acktr': lambda e: ACKTR(policy="MlpPolicy", env=e,
                             learning_rate=5e-4, n_steps=1).learn(total_timesteps=20000, seed=0),
    'dqn': lambda e: DQN(policy="MlpPolicy", batch_size=16, gamma=0.1,
                         exploration_fraction=0.001, env=e).learn(total_timesteps=40000, seed=0),
    'ppo1': lambda e: PPO1(policy="MlpPolicy", env=e, lam=0.5,
                           optim_batchsize=16, optim_stepsize=1e-3).learn(total_timesteps=15000, seed=0),
    'ppo2': lambda e: PPO2(policy="MlpPolicy", env=e,
                           learning_rate=1.5e-3, lam=0.8).learn(total_timesteps=20000, seed=0),
    'trpo': lambda e: TRPO(policy="MlpPolicy", env=e,
                           max_kl=0.05, lam=0.7).learn(total_timesteps=10000, seed=0),
}


def test_env(model_name):
    """
    Test if the algorithm (with a given policy)
    can learn an identity transformation (i.e. return observation as an action)
    :param model_name: (str) Name of the RL model
    """
    env = DummyVecEnv([lambda: SlayTheScriptEnv()])
    model = LEARN_FUNC_DICT[model_name](env)
    n_trials = 1000
    reward_sum = 0
    set_global_seeds(0)
    obs = env.reset()
    for _ in range(n_trials):
        action, _ = model.predict(obs)
        obs, reward, _, _ = env.step(action)
        reward_sum += reward
    # Free memory
    del model, env

test_env('dqn')
