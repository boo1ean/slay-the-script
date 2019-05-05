import json
import logging

import random
from tabulate import tabulate
from fabulous.color import bold, magenta_bg, green_bg, red_bg, red, green, magenta, blue

from getch import getch
from subprocess import call
from time import sleep
import os

def clear_screen():
    _ = call('clear' if os.name =='posix' else 'cls')

# Actions space:
# - play card 0,1,2,3,4,5,6,7,8,9
# - end turn

# World state
# - hp hero
# - hp enemy
# - draw pile
# - discard pile
# - hand (10 cards)
# - enemy intention
# - current energy

with open('cards.json', 'r') as cards_file:
    cards = json.loads(cards_file.read())

decorations = [None, green, red, red]
def get_text_decoration(config):
    return decorations[config['id']]

class Card():
    def __init__(self, config):
        self.config = dict(config)
        self.text_decoration = get_text_decoration(config)

    def effect(self):
        return self.config

    def render(self):
        return self.text_decoration(self.config['name'])

    def get_cost(self):
        return self.config['cost']

    cost = property(get_cost)

class Creature():
    def is_dead(self):
        return self.hp <= 0

    def apply_damage(self, amount):
        if self.block:
            amount -= self.block
        if amount > 0:
            self.hp -= amount

    def is_player(self):
        return False


DEFAULT_PALYER_HP = 70
DEFAULT_PLAYER_ENERGY = 3
DEFAULT_PLAYER_BLOCK = 0
DEFAULT_PLAYER_DRAW_RATE = 5

class Player(Creature):
    # default deck is 6 defends + 6 strikes
    default_deck = [Card(cards[0])] * 6 + [Card(cards[1])] * 6 + [Card(cards[2])] * 2

    # Initiall put whole deck to discard pile
    # and after initialization shuffle it to the draw pile
    def __init__(self, deck = default_deck, name = 'Naive-player'):
        self.name = name
        self.deck = deck
        self.discard_pile = deck
        self.draw_pile = []
        self.hand = []
        self.draw_rate = DEFAULT_PLAYER_DRAW_RATE

        self.hp = DEFAULT_PALYER_HP
        self.max_hp = DEFAULT_PALYER_HP
        self.energy = DEFAULT_PLAYER_ENERGY
        self.max_energy = DEFAULT_PLAYER_ENERGY
        self.block = DEFAULT_PLAYER_BLOCK

        self.shuffle_discard_pile_to_draw_pile()

    def get_hand_card(self, index):
        try:
            card = self.hand[index]
            return card.config['id']
        except IndexError:
            return 0

    def is_player(self):
        return True

    # Shuffle cards in discard pile
    # and move it to draw pile
    def shuffle_discard_pile_to_draw_pile(self):
        random.shuffle(self.discard_pile)
        self.draw_pile = self.discard_pile
        self.discard_pile = []

    # Put DRAW_RATE cards from draw pile into hand
    # if there are not enough cards for draw session
    # put discard pile into draw pile and continue
    def draw(self, cards_to_draw):
        self.hand = self.hand + self.draw_pile[0:cards_to_draw]
        self.draw_pile = self.draw_pile[cards_to_draw:]

        if len(self.hand) < cards_to_draw:
            self.shuffle_discard_pile_to_draw_pile()
            self.draw(cards_to_draw - len(self.hand))

    # Move cards from hand to discard pile
    def discard_hand(self):
        self.discard_pile += self.hand
        self.hand = []

    def new_turn(self):
        self.discard_hand()
        self.draw(self.draw_rate)
        self.energy = self.max_energy
        self.block = DEFAULT_PLAYER_BLOCK

    def play_card(self, index):
        # Card index is out of range
        if index >= len(self.hand):
            return None

        card = self.hand[index]

        # Not enough energy
        if card.cost > self.energy:
            return None

        # Actually play card
        self.energy -= card.cost
        self.discard_card_from_hand(index)
        return card.effect()


    def discard_card_from_hand(self, index):
        card = self.hand[index]
        del self.hand[index]
        self.discard_pile += [card]


    def inc_block(self, block):
        self.block += block


    # CLI render
    def render(self):
        draw_pile = list(map(lambda c: c.render(), self.draw_pile))
        # hand = list(map(lambda c: c.render(), enumerate(self.hand))
        hand = ['%d) %s' % (i + 1, c.render()) for i, c in enumerate(self.hand)]
        discard_pile = list(map(lambda c: c.render(), self.discard_pile))

        columns = {}
        columns[bold('Hand (%d)' % len(hand))] = hand
        columns[''] = ['\t\t\t']
        columns[bold('Draw pile (%d)' % len(draw_pile))] = draw_pile
        columns[bold('Discard pile (%d)' % len(discard_pile))] = discard_pile
        deck_state = tabulate(columns, headers='keys', tablefmt="plain")

        status_bar = bold('%s ❤️ %s/%s ⚡%s/%s' % (bold(self.name), red(self.hp), red(self.max_hp), blue(self.energy), blue(self.max_energy)))
        if self.block > 0:
            status_bar += ' 🛡️ %s' % bold(self.block)

        return '%s\n\n%s' % (status_bar, deck_state)


DEFAULT_ENEMY_HP = 52
DEFAULT_ENEMY_BLOCK = 0

class Enemy(Creature):
    def __init__(self, name = 'Script-killer'):
        self.name = name
        self.hp = DEFAULT_ENEMY_HP
        self.max_hp = DEFAULT_ENEMY_HP
        self.block = DEFAULT_ENEMY_BLOCK
        self.action = Card(cards[1])
        self.buff = 3

    def act(self):
        eff = self.action.effect()
        eff['damage'] += self.buff
        return eff

    def get_damage_intent(self):
        return self.action.effect()['damage']

    def render(self):
        hp_bar = bold('%s ❤️ %s/%s' % (bold(self.name), red(self.hp), red(self.max_hp)))
        intent = 'Going to deal %s %s' % (red(self.action.effect()['damage']), red('damage'))

        return '%s\n%s' % (hp_bar, intent)

    damage_intent = property(get_damage_intent)

class Battle():
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def render(self):
        return '%s\n\n\n%s' % (self.player.render(), self.enemy.render())

    def start(self):
        self.player.draw(5)

    def step(self, action):
        try:
            index = int(action)

            if index == 5:
                return self.end_turn()

            effect = self.player.play_card(index)
            if effect:
                self.apply_effect(self.player, self.enemy, effect)

        except ValueError:
            return None

    def apply_effect(self, source, target, effect):
        if 'damage' in effect:
            target.apply_damage(effect['damage'])

        if 'block' in effect:
            source.inc_block(effect['block'])

        return None

    def end_turn(self):
        enemy_effect = self.enemy.act()
        self.apply_effect(self.enemy, self.player, enemy_effect)
        self.player.new_turn()

    def has_winner(self):
        if self.player.is_dead():
            return self.enemy
        if self.enemy.is_dead():
            return self.player
        return None

import gym
from gym import spaces


N_DISCRETE_ACTIONS = 6
N_DISCRETE_OBSERVATIONS=13

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
            len(cards), #card1
            len(cards), #card2
            len(cards), #card3
            len(cards), #card4
            len(cards), #card5
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

        # if mana is used and no end turn - bad
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

# env = SlayTheScriptEnv()
# print(env.step(1))

# class UserActor():
    # def __init__(self):


# p = Player()
# e = Enemy()
# b = Battle(player = p, enemy = e)

# clear_screen()
# done = False
# b.start()
# while not done:
    # print(b.render())
    # print('''
              # ____      ________
            # ,^.__.>--"~~'_.--~_)~^.
           # _L^~   ~    (~ _.-~ \. |\\
        # ,-~    __    __,^"/\_A_/ /' \\
      # _/    ,-"  "~~" __) \  ~_,^   /\\
     # //    /  ,-~\ x~"  \._"-~     ~ _Y
     # Y'   Y. (__.//     /  " , "\_r ' ]
     # J-.__l_>---r{      ~    \__/ \_ _/
    # (_ (   (~  (  ~"---   _.-~ `\ / \ !
     # (_"~--^----^--------"  _.-c Y  /Y'
      # l~---v----.,______.--"  /  !_/ |
       # \.__!.____./~-.      _/  /  \ !
        # `x._\_____\__,>---"~___Y\__/Y'
            # ~     ~(_~~(_)"~___)/ /\|
                   # (_~~   ~~___)  \_t
                   # (_~~   ~~___)\_/ |
                   # (_~~   ~~___)\_/ |
                   # { ~~   ~~   }/ \ l
    # ''')
    # action = getch()
    # b.step(action)
    # clear_screen()
    # winner = b.has_winner()
    # if winner:
        # done = True
        # print('Winner is %s' % bold(winner.name))



# p.draw(5)
# p.play_card(0)
# p.play_card(0)
# p.play_card(0)
# print(p.render())

# print(e.act())


