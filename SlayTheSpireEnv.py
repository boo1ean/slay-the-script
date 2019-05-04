import json
import random
import logging
from tabulate import tabulate
from fabulous.color import bold, magenta_bg, green_bg, red_bg, red, green, magenta

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
# - current mana

with open('cards.json', 'r') as cards_file:
    cards = json.loads(cards_file.read())

decorations = [green, red]
def get_text_decoration(config):
    return decorations[config['id']]

class Card():
    def __init__(self, config):
        self.config = config
        self.text_decoration = get_text_decoration(config)

    def render(self):
        return self.text_decoration(self.config['name'])

DEFAULT_PALYER_HP = 70
DEFAULT_PLAYER_MANA = 3
DEFAULT_PLAYER_DRAW_RATE = 5

class Player():
    # default deck is 6 strikes + 6 defends
    default_deck = [Card(cards[0])] * 6 + [Card(cards[1])] * 6

    # Initiall put whole deck to discard pile
    # and after initialization shuffle it to the draw pile
    def __init__(self, deck = default_deck):
        self.deck = deck
        self.discard_pile = deck
        self.draw_pile = []
        self.hand = []
        self.draw_rate = DEFAULT_PLAYER_DRAW_RATE
        self.hp = DEFAULT_PALYER_HP
        self.mana = DEFAULT_PLAYER_MANA
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


    # CLI render
    def render(self):
        draw_pile = list(map(lambda c: c.render(), self.draw_pile))
        hand = list(map(lambda c: c.render(), self.hand))
        discard_pile = list(map(lambda c: c.render(), self.discard_pile))

        columns = {}
        columns["Draw pile (%d)" % len(draw_pile)] = draw_pile
        columns["Hand (%d)" % len(hand)] = hand
        columns["Discard pile (%d)" % len(discard_pile)] = discard_pile

        return tabulate(columns, headers="keys")

DEFAULT_ENEMY_HP = 52

class Enemy():
    def __init__(self):
        self.hp = DEFAULT_ENEMY_HP


class Battle():
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy


p = Player()
p.draw(5)
p.draw(5)
p.discard_hand()
p.draw(5)
print(p.render())
