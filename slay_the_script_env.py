from py4j.java_gateway import JavaGateway
gateway = JavaGateway()
m = gateway.entry_point

import gym
from gym import spaces

# 5 cards + end turn
N_DISCRETE_ACTIONS = 6

PLAYER_HEALTH = 0
PLAYER_BLOCK = 1
PLAYER_ENERGY = 2
PLAYER_MAX_ENERGY = 3
CARD_SLOT_0 = 4
CARD_SLOT_1 = 5
CARD_SLOT_2 = 6
CARD_SLOT_3 = 7
CARD_SLOT_4 = 8
ENEMY_HEALTH = 9
ENEMY_BLOCK = 10
ENEMY_DAMAGE_INTENT = 11

# hp, max_hp, block, energy, max_energy, card1..card5, enemy_hp, enemy_max_hp, enemy_damange_intent
class SlayTheScriptEnv(gym.Env):
    def __init__(self):
        super(SlayTheScriptEnv, self).__init__()
        self.reset()
        self.m = m

        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)
        self.observation_space = spaces.MultiDiscrete([
            100, # player hp
            100, # player block
            3, # player energy
            3, # player max_energy
            100, # card slot 0
            100, # card slot 1
            100, # card slot 2
            100, # card slot 3
            100, # card slot 4
            100, # enemy hp
            100, # enemy block
            100, # enemy_damage_intent
        ])


    def step(self, action):
        assert self.action_space.contains(action)
        print("Step action:", action)
        state = list(m.getState())
        action = int(action)

        done = False
        reward = 0
        info = {}

        # if energy wasn't used - too bad
        if action == 5 and state[PLAYER_ENERGY] > 0:
            reward = -1

        # if energy is used and no end turn - bad
        if action != 5 and state[PLAYER_ENERGY] == 0:
            reward = -1

        # if try to play empty card slot - bad
        if action != 5 and state[CARD_SLOT_0 + action] == 0:
            reward = -1

        if action == 5:
            m.endTurn()
        else:
            if m.canPlayCard(action):
                m.playCard(action)
            else:
                reward = -1;

        print("Waiting for completed actions")
        m.waitUntilActionsCompleted()
        print("Actions completed")
        state = m.getState()

        if state[PLAYER_HEALTH] == 0:
            reward = -5
            done = True
        else:
            if state[ENEMY_HEALTH] == 0:
                reward = 1 + 10 * state[PLAYER_HEALTH] / 100
                done = True

        return self._get_obs(), reward, done, info

    def reset(self):
        print("Env reset:")
        m.abandonRun()
        m.startGame()
        m.completeDialog()
        m.enterFirstRoom()
        m.waitForDraw()
        return self._get_obs()

    def _get_obs(self):
        return list(m.getState())

# e = SlayTheScriptEnv()
# print(e.step(0))
# print(e.step(0))
# print(e.step(0))
# print(e.step(5))
# print(e.step(0))
# print(e.step(0))
# print(e.step(0))
# print(e.step(5))
# print(e.step(0))
# print(e.step(0))
# print(e.step(0))
# print(e.step(5))
# print(e.step(0))
# print(e.step(0))
# print(e.step(0))
# print(e.step(5))
# print(e.step(0))
# print(e.step(0))
# print(e.step(0))
# print(e.step(5))
