from world_loader import World
from ship import Ship
from player import Player
import ui
import os

def print_help():
    print("\n--- COMMANDS ---")
    print("Movement: north, south, east, west (or n, s, e, w)")
    print("Actions: get [item], drop [item], examine [item], look, use [item], search, talk")
    print("Systems: inv, save, quit")
    print("----------------\n")

def get_dialogue(character, room_id, player_visited_triggers, dialogue_data):
    key = room_id.lower().replace(" ", "_")
    if character not in dialogue_data or key not in dialogue_data[character]:
        return None

    options = dialogue_data[character][key]
    # Priority check for new lines
    for line in sorted(options, key=lambda x: x['priority']):
        if line['trigger'] not in player_visited_triggers:
            if not line['repeatable']:
                player_visited_triggers.add(line['trigger'])
            return line['line']

    # Fallback to repeatable lines
    fallback = next((l for l in options if l['repeatable']), None)
    return fallback['line'] if fallback else None

def main():
    ui.display_splash()
    # 1. WORLD SELECTION LAUNCHER
    available_worlds = World.list_available_worlds()
    if not available_worlds:
        print("Error: No world folders found in /worlds/.")
        return

    print("\n==== TEXT ADVENTURE GAME ENGINE ===\n\n           Copyright 2026")
    for i, w in enumerate(available_worlds, 1):
        print(f"{i}. {w.replace('_', ' ').title()}")

    world_idx = int(input("\nSelect World: ")) - 1
    selected_world = available_worlds[world_idx]

    # 2. INITIALIZE WORLD & PLAYER
    world = World(selected_world)
    save_path = f"{selected_world}_save.json"

    if os.path.exists(save_path):
        choice = input("Save file detected. Load game? (y/n): ").lower()
        if choice == 'y':
            player_data = world.load_game_state()
            player = Player(start_pos=player_data["position"])
            player.health = player_data["health"]
            player.inventory = player_data["inventory"]
            player.visited = set(tuple(p) for p in player_data["visited"])
            player.revealed_coords = set(tuple(p) for p in player_data["revealed"])
            player.visited_dialogue = set(player_data.get("dialogue_history", []))
            print("Game Loaded.")
        else:
            world.load_initial_data()
            p_data = next(i for i in world.items if i.get("type") == "player")
            player = Player(start_pos=p_data["start_pos"])
            player.visited_dialogue = set()
    else:
        world.load_initial_data()
        p_data = next(i for i in world.items if i.get("type") == "player")
        player = Player(start_pos=p_data["start_pos"])
        player.visited_dialogue = set()

    ship = Ship(world.map, world.items)

    COMMAND_MAP = {
        "n": "north", "north": "north", "s": "south", "south": "south",
        "e": "east", "east": "east", "w": "west", "west": "west",
        "i": "inv", "inventory": "inv", "l": "look", "look": "look",
        "x": "examine", "examine": "examine", "g": "get", "get": "get",
        "u": "use", "use": "use", "d": "drop", "drop": "drop",
        "h": "help", "help": "help", "search": "search", "talk": "talk"
    }

    while True:
        ui.clear_screen()
        ui.render_map(ship, player, world.items, world.active_enemies)

        current_room_id = ship.current_room(player.position)

        # --- STORY TRIGGERS ---
        # Rachel Rescue Logic
        if current_room_id == "med_bay":
            rachel_in_inv = next((i for i in player.inventory if i['id'] == "rachel"), None)
            if rachel_in_inv:
                player.inventory.remove(rachel_in_inv)
                rachel_in_inv['position'] = list(player.position)
                world.items.append(rachel_in_inv)
                ui.display_message("Ryan: 'You're safe now, Rachel.'")
                ui.display_message("Rachel: 'Thank you. I can coordinate from here.'")

        # Dialogue Auto-Triggers
        ryan_msg = get_dialogue("ryan", current_room_id, player.visited_dialogue, world.dialogue)
        if ryan_msg: ui.display_message(f"Ryan: *{ryan_msg}*")

        # --- INPUT HANDLING ---
        raw_input = input(f"\n{player.position} HP:{player.health} > ").lower().strip()
        if not raw_input: continue

        if raw_input == "save":
            world.save_game_state(player)
            continue
        elif raw_input == "quit":
            break

        parts = raw_input.split(maxsplit=1)
        verb = COMMAND_MAP.get(parts[0], parts[0])
        target = parts[1] if len(parts) > 1 else None

        # --- EXECUTION LOGIC ---
        if verb in ["north", "south", "east", "west"]:
            success, err = player.move(verb[0], ship)
            if success:
                enemy = next((e for e in world.active_enemies if e.pos == player.position and e.alive), None)
                if enemy:
                    ui.display_message(f"(!) A {enemy.name} emerges!")
                    if not enemy.fight(player):
                        print("\n--- CRITICAL FAILURE: SYSTEM OFFLINE ---")
                        break
            else:
                ui.display_message(err)

        elif verb == "talk":
            r_present = any(i['id'] == "rachel" for i in world.items if tuple(i.get("position", [])) == player.position) or \
                        any(i['id'] == "rachel" for i in player.inventory)
            if r_present:
                ui.display_message("Rachel: 'We need to restore power to the bridge if we want to get out of here.'")
            else:
                ui.display_message("Only the echo of the ship answers you.")

        elif verb == "get":
            # Check for Rachel/NPCs first
            item = next((i for i in world.items if (not target or i['name'].lower() == target)
                         and tuple(i.get("position", [])) == player.position), None)
            if item:
                if item.get("type") == "npc":
                    ui.display_message(f"You help {item['name']} up.")
                    player.add_item(item)
                    world.items.remove(item)
                elif player.add_item(item):
                    world.items.remove(item)
                    ui.display_message(f"Picked up {item['name']}.")
            else:
                ui.display_message("Nothing here to pick up.")

        elif verb == "use":
            item = next((i for i in player.inventory if i['name'].lower() == (target or "")), None)
            if item and (item.get("type") == "consumable" or "heal" in item):
                player.health = min(100, player.health + item.get("heal", 25))
                player.inventory.remove(item)
                ui.display_message(f"Used {item['name']}. HP: {player.health}")
            else:
                ui.display_message("You can't use that right now.")

        elif verb == "look":
            desc = world.map.get(current_room_id, {}).get("desc", "A dark room.")
            ui.display_message(desc)
            room_items = [i['name'] for i in world.items if tuple(i.get("position", [])) == player.position]
            if room_items: ui.display_message(f"Items here: {', '.join(room_items)}")

        elif verb == "inv":
            ui.display_message("Inventory: " + (", ".join([i['name'] for i in player.inventory]) if player.inventory else "Empty"))

        elif verb == "help":
            print_help()

if __name__ == "__main__":
    main()
