import json
import random
import logging
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

decorations = [green, red]
def get_text_decoration(config):
    return decorations[config['id']]

class Card():
    def __init__(self, config):
        self.config = config
        self.text_decoration = get_text_decoration(config)

    def effect(self):
        return self.config

    def render(self):
        return self.text_decoration(self.config['name'])

    def get_cost(self):
        return self.config['cost']

    cost = property(get_cost)

DEFAULT_PALYER_HP = 70
DEFAULT_PLAYER_ENERGY = 3
DEFAULT_PLAYER_BLOCK = 10
DEFAULT_PLAYER_DRAW_RATE = 5

class Player():
    # default deck is 6 defends + 6 strikes
    default_deck = [Card(cards[0])] * 6 + [Card(cards[1])] * 6

    # Initiall put whole deck to discard pile
    # and after initialization shuffle it to the draw pile
    def __init__(self, deck = default_deck, name = 'Naive player'):
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
        hand = ['%d) %s' % (i, c.render()) for i, c in enumerate(self.hand)]
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

class Enemy():
    def __init__(self):
        self.name = 'Script-killer'
        self.hp = DEFAULT_ENEMY_HP
        self.max_hp = DEFAULT_ENEMY_HP
        self.action = Card(cards[1])

    def act(self):
        return self.action.effect()

    def render(self):
        hp_bar = bold('%s ❤️ %s/%s' % (bold(self.name), red(self.hp), red(self.max_hp)))
        intent = 'Going to deal %s %s' % (red(self.action.effect()['damage']), red('damage'))

        return '%s\n%s' % (hp_bar, intent)

class Battle():
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def render(self):
        return '%s\n\n\n%s' % (self.player.render(), self.enemy.render())

    def start(self):
        self.player.draw(5)

# class UserActor():
    # def __init__(self):


p = Player()
e = Enemy()
b = Battle(player = p, enemy = e)

clear_screen()
done = False
b.start()
while not done:
    print(b.render())
    ch = getch()
    clear_screen()
    print(ch)



# p.draw(5)
# p.play_card(0)
# p.play_card(0)
# p.play_card(0)
# print(p.render())

# print(e.act())


