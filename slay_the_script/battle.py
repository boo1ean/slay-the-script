class Battle():
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

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

    def render(self):
        return '%s\n\n\n%s' % (self.player.render(), self.enemy.render())
