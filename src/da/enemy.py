# enemy.py — Defines enemy behavior and types
import random

class Enemy:
    def __init__(self, name, health, attack_power, enemy_type):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.enemy_type = enemy_type

    def is_alive(self):
        """Check if the enemy is still alive."""
        return self.health > 0

    def attack(self):
        """Perform an attack with randomized power."""
        return random.randint(1, self.attack_power)

    def take_damage(self, damage):
        """Apply damage and return updated health."""
        self.health -= damage
        return self.health

class Scuttler(Enemy):
    def __init__(self):
        super().__init__(
            name="Scuttler",
            health=10,
            attack_power=4,
            enemy_type="scuttler"
        )

class Lurker(Enemy):
    def __init__(self):
        super().__init__(
            name="Lurker",
            health=25,
            attack_power=12,
            enemy_type="lurker"
        )

class Stalker(Enemy):
    def __init__(self):
        super().__init__(
            name="The Stalker",
            health=60,
            attack_power=18,
            enemy_type="stalker"
        )

    def ryan_chance_to_win(self):
        """25% chance for Ryan to win against The Stalker."""
        return random.random() < 0.25
