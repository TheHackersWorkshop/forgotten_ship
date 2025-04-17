# combat.py — Manages combat between player and enemy
import random
from .player import Player
from .enemy import Scuttler, Lurker, Stalker

def combat(player, enemy):
    """Handles combat sequence between player and enemy."""
    print(f"\n⚔️  A wild {enemy.name} appears!")

    while player.health > 0 and enemy.is_alive():
        # Player's turn to attack (randomized damage between 5 and 15)
        player_attack = random.randint(5, 15)
        enemy.take_damage(player_attack)
        print(f"You hit the {enemy.name} for {player_attack} damage.")

        # Check if enemy is defeated after player's attack
        if not enemy.is_alive():
            print(f"The {enemy.name} has been defeated!")
            return True

        # Enemy's counterattack
        enemy_attack = enemy.attack()
        player.health -= enemy_attack
        print(f"The {enemy.name} hits you for {enemy_attack} damage.")
        print(f"Your health is now {player.health}.")

    # If player’s health reaches 0, the player dies
    if player.health <= 0:
        print("💀 You have been killed by the enemy.")
        return False
