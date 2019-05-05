import gym
from gym import spaces

from .player import Player
from .battle import Battle
from .enemy import Enemy
from .card import Card

# 5 cards + end turn
N_DISCRETE_ACTIONS = 6

# hp, max_hp, block, energy, max_energy, card1..card5, enemy_hp, enemy_max_hp, enemy_damange_intent
class SlayTheScriptEnv(gym.Env):
    def __init__(self):
        super(SlayTheScriptEnv, self).__init__()
        self.reset()
        self.action_space = spaces.Discrete(N_DISCRETE_ACTIONS)

        self.observation_space = spaces.MultiDiscrete([
            self.player.max_hp, #hp
            self.player.max_hp, #max_hp
            15, #block
            3, #energy
            3, #max_energy
            len(Card.cards), #card1
            len(Card.cards), #card2
            len(Card.cards), #card3
            len(Card.cards), #card4
            len(Card.cards), #card5
            self.enemy.max_hp, #enemy_hp
            self.enemy.max_hp, #enemy_max_hp
            100, #enemy_max_hp
        ])

    def step(self, action):
        assert self.action_space.contains(action)
        reward = 0
        info = {}

        # if energy wasn't used - too bad
        if action == 5 and self.player.energy > 0:
            reward = -1

        # if energy is used and no end turn - bad
        if action != 5 and self.player.energy == 0:
            reward = -1

        # if try to play empty card slot - bad
        if action != 5 and self.player.get_hand_card(action) == 0:
            reward = -1

        self.battle.step(action)
        winner = self.battle.has_winner()

        if winner and winner.is_player():
            reward = 1 + 10 * winner.hp / winner.max_hp
            info['winner'] = winner.name

        return self._get_obs(), reward, bool(winner), info

    def reset(self):
        self.player = Player()
        self.enemy = Enemy()
        self.battle = Battle(player = self.player, enemy = self.enemy)
        self.battle.start()
        return self._get_obs()

    def _get_obs(self):
        return (
            self.player.hp,
            self.player.max_hp,
            self.player.block,
            self.player.energy,
            self.player.max_energy,
            self.player.get_hand_card(0),
            self.player.get_hand_card(1),
            self.player.get_hand_card(2),
            self.player.get_hand_card(3),
            self.player.get_hand_card(4),
            self.enemy.hp,
            self.enemy.max_hp,
            self.enemy.damage_intent,
        )

    def render(self):
        return self.battle.render()
