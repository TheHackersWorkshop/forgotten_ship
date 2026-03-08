import random

class Enemy:
    def __init__(self, data):
        self.name = data.get("name", "Unknown Creature")
        self.health = data.get("health", 50)
        self.atk = data.get("atk", 10)
        self.pos = tuple(data.get("location", (0, 0)))
        self.alive = True

    def fight(self, player):
        print(f"\n[!!!] ENCOUNTER: {self.name.upper()} [!!!]")

        # Track previous position for the "Run" mechanic
        prev_pos = player.last_position if hasattr(player, 'last_position') else player.position

        while self.health > 0 and player.health > 0:
            print(f"\n{self.name} HP: {self.health} | Your HP: {player.health}")
            choice = input("Actions: (F)ight, (R)un, (H)eal > ").lower().strip()

            if choice == 'f':
                # Check if player has the baton
                weapon = next((i for i in player.inventory if i.get("id") == "shock_baton"), None)
                base_dmg = weapon.get("damage", 3) if weapon else 2 # Punching does less damage

                player_dmg = random.randint(base_dmg, base_dmg + 5)
                self.health -= player_dmg
                print(f" >> You strike with {weapon['name'] if weapon else 'your fists'} for {player_dmg}!")

            elif choice == 'r':
                # 2. RUN: Move away from the monster
                print(f" >> You scramble back to your previous position!")
                player.position = prev_pos
                return True # Exit combat, player lives

            elif choice == 'h':
                # Search inventory for an item where type is 'consumable' and it has a 'heal' value
                medkit = next((i for i in player.inventory if i.get("type") == "consumable" and "heal" in i), None)

                if medkit:
                    heal_amt = medkit.get("heal", 20) # Defaults to 20 if heal value is missing
                    player.health = min(100, player.health + heal_amt)
                    player.inventory.remove(medkit)
                    print(f" >> Used {medkit['name']}. Restored {heal_amt} HP!")

                    # Enemy gets a move while you heal
                    enemy_dmg = random.randint(1, self.atk)
                    player.health -= enemy_dmg
                    print(f" >> The {self.name} hits you for {enemy_dmg} while you're distracted!")
                else:
                    print(" >> You don't have any Medkits!")


            else:
                print(" >> Invalid choice. The monster glares at you.")

        if self.health <= 0:
            self.alive = False
            print(f"\n >> The {self.name} has been slain!")
            return True # Player won

        return False # Player died
