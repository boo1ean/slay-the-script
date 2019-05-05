import json
from fabulous.color import bold, magenta_bg, green_bg, red_bg, red, green, magenta, blue

with open('cards.json', 'r') as cards_file:
    cards = json.loads(cards_file.read())

decorations = [None, green, red, red]
def get_text_decoration(config):
    return decorations[config['id']]

class Card():
    cards = cards
    def createById(id):
        return Card(cards[id - 1])

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
