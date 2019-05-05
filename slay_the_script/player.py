import random
from tabulate import tabulate
from fabulous.color import bold, red, green, blue

from .card import Card
from .creature import Creature


DEFAULT_PALYER_HP = 70
DEFAULT_PLAYER_ENERGY = 3
DEFAULT_PLAYER_BLOCK = 0
DEFAULT_PLAYER_DRAW_RATE = 5

class Player(Creature):
    # default deck is 6 defends + 6 strikes
    default_deck = [Card.createById(1)] * 6 + [Card.createById(2)] * 6 + [Card.createById(3)] * 2

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

