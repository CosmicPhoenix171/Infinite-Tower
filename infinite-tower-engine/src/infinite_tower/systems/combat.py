class CombatSystem:
    def __init__(self):
        self.damage_multiplier = 1.0

    def calculate_damage(self, base_damage, enemy_defense):
        effective_damage = base_damage * self.damage_multiplier - enemy_defense
        return max(effective_damage, 0)

    def perform_attack(self, attacker, defender):
        damage = self.calculate_damage(attacker.attack_power, defender.defense)
        defender.health -= damage
        return damage

    def is_enemy_defeated(self, enemy):
        return enemy.health <= 0

    def apply_damage_over_time(self, target, damage_per_second, duration):
        total_damage = damage_per_second * duration
        target.health -= total_damage
        return total_damage

    def heal(self, target, heal_amount):
        target.health += heal_amount
        return heal_amount