import json
import os
import random

class Enemy:
    def __init__(self, name, health, attack_power, enemy_type):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.enemy_type = enemy_type

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0

    def attack(self):
        return random.randint(1, self.attack_power)

def fight(player, enemy):
    """Accepts either an Enemy instance or a dict describing an enemy.
    If a dict is provided, we create a temporary Enemy to run the fight and
    then update the dict with the result (health and alive flag).
    """
    using_dict = False
    if isinstance(enemy, dict):
        using_dict = True
        e = Enemy(enemy["name"], enemy.get("health", 1), enemy.get("attack_power", 1), enemy.get("enemy_type"))
    else:
        e = enemy

    print(f"A {e.name} attacks!")

    while e.is_alive() and player.health > 0:
        dmg = e.attack()
        player.health -= dmg
        print(f"The {e.name} hits you for {dmg}.")

        if player.health <= 0:
            return False

        e.take_damage(10)
        print(f"You hit the {e.name} for 10.")

    print(f"The {e.name} is dead.")
    if using_dict:
        enemy["health"] = e.health
        enemy["alive"] = False
        enemy["location"] = None
    return True

def load_enemies(world_name):
    path = os.path.join("worlds", world_name, "enemies.json")
    if not os.path.exists(path):
        return []
    data = json.load(open(path, "r"))
    enemies = []
    for e in data:
        enemies.append(Enemy(e["name"], e["health"], e["attack_power"], e["enemy_type"]))
    return enemies


def manhattan(a, b):
    return abs(ord(a[0]) - ord(b[0])) + abs(a[1] - b[1])


def step_towards(src, dest):
    sc, sr = src
    dc, dr = dest
    nc = sc
    nr = sr
    if sc != dc:
        nc = chr(ord(sc) + (1 if ord(dc) > ord(sc) else -1))
    elif sr != dr:
        nr = sr + (1 if dr > sr else -1)
    return (nc, nr)


def update_enemies(world, ship, player):
    """Move enemies along patrols or towards player when in agro range.
    If an enemy reaches the player, trigger a fight.
    """
    for e in world.enemies:
        if not e.get('alive', True):
            continue
        loc = e.get('location')
        if not loc:
            continue
        loc_t = tuple(loc)
        # Patrol path
        path = e.get('path')
        if path:
            idx = e.get('patrol_index', 0)
            idx = (idx + 1) % len(path)
            e['patrol_index'] = idx
            e['location'] = list(path[idx])
            loc_t = tuple(e['location'])
        else:
            # proximity agro
            agro = e.get('agro_range', 0)
            if agro and manhattan(loc_t, player.position) <= agro:
                    newpos = step_towards(loc_t, player.position)
                    # only move if walkable (if ship provided)
                    if (ship is None) or ship.is_walkable(newpos):
                        e['location'] = list(newpos)
                        loc_t = tuple(e['location'])
        # check if in same tile as player -> fight
        if loc_t == player.position:
            print(f"A {e.get('name')} attacks by proximity!")
            alive = fight(player, e)
            if not alive:
                print('You died. Game over.')
                return False
            else:
                e['alive'] = False
                e['location'] = None
    return True
