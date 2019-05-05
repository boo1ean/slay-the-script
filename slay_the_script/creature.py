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

