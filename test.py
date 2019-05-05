import gym

import os
from getch import getch

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from slay_the_script.env import SlayTheScriptEnv

from subprocess import call
from time import sleep

def clear_screen():
    _ = call('clear' if os.name =='posix' else 'cls')

env = SlayTheScriptEnv()
env = DummyVecEnv([lambda: env])

model = PPO2(MlpPolicy, env, verbose=0)
model.learn(total_timesteps=100_000)

while True:
    obs = env.reset()
    clear_screen()
    done = False
    action = None
    while not done:
        print('Previous action: %s' % action)
        print(env.render())
        getch()
        action, _states = model.predict(obs)
        obs, rewards, done, info = env.step(action)
        clear_screen()
        if done:
            print(info)
            getch()
