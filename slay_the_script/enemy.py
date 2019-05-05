from fabulous.color import bold, red

from .creature import Creature
from .card import Card


DEFAULT_ENEMY_HP = 52
DEFAULT_ENEMY_BLOCK = 0

class Enemy(Creature):
    def __init__(self, name = 'Script-killer'):
        self.name = name
        self.hp = DEFAULT_ENEMY_HP
        self.max_hp = DEFAULT_ENEMY_HP
        self.block = DEFAULT_ENEMY_BLOCK
        self.action = Card.createById(2)
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

