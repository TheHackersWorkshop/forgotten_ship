from world_loader import World
from ship import Ship
from player import Player
from puzzles import PuzzleManager
from enemy import fight as enemy_fight, update_enemies
from ui import render_map, show_help, save_game, load_game, show_dialogue

WORLD = "derelict_ship"

def main():
    world = World(WORLD, new_game=True)
    ship = Ship(world.map, world.items)

    # Load player from items.json (constant player)
    player_data = next(
        item for item in world.items
        if item.get("type") == "player"
    )
    player = Player(
        start_pos=player_data["start_pos"],
        world_name=WORLD
    )

    print("You wake up alone on a derelict ship.")
    show_help()

    # Puzzle manager
    pm = PuzzleManager(WORLD)
    # If world has saved puzzle state, sync it into PuzzleManager
    if getattr(world, "puzzles", None):
        if isinstance(world.puzzles, list):
            pm.puzzles = {p["id"]: p for p in world.puzzles}
        elif isinstance(world.puzzles, dict):
            pm.puzzles = world.puzzles

    while True:
        render_map(ship, player, world.items)
        cmd = input("> ").lower().strip()

        if cmd in ("n", "s", "e", "w"):
            dialogue, error = player.move(cmd, ship)

            if error:
                print(error)
            else:
                # Pickup items on current tile
                for item in list(world.items):
                    pos = item.get("position")
                    if pos and tuple(pos) == player.position and item.get("id") != "player":
                        ok = player.add_item(item)
                        if ok:
                            item["position"] = None
                            print(f"You picked up {item['name']}.")
                        else:
                            print("Inventory full. Consider dropping something or use storage.")

                # Check for enemy encounters
                for enemy in world.enemies:
                    if enemy.get("location") and tuple(enemy["location"]) == player.position and enemy.get("alive", True):
                        alive = enemy_fight(player, enemy)
                        if not alive:
                            print("You died. Game over.")
                            return
                        else:
                            enemy["alive"] = False
                            enemy["location"] = None

                if dialogue:
                    show_dialogue(dialogue)

                # After player's action, update enemies (patrols / proximity)
                cont = update_enemies(world, ship, player)
                if cont is False:
                    return

        elif cmd == "help":
            show_help()

        elif cmd == "inventory":
            if not player.inventory:
                print("Inventory is empty.")
            else:
                print("Inventory:")
                for it in player.inventory:
                    qty = it.get('quantity') if it.get('type') == 'consumable' else 1
                    print(f" - {it.get('name')} ({it.get('id')}) x{qty} - {it.get('description', '')}")
                print(f"Slots: {len(player.inventory)}/{player.max_inventory}")

        elif cmd.startswith("use "):
            arg = cmd[4:].strip()
            found = None
            for it in list(player.inventory):
                if it.get("id") == arg or it.get("name", "").lower() == arg.lower():
                    found = it
                    break
            if not found:
                print("You don't have that item.")
            else:
                # If using a key, confirm removal
                if found.get('type') == 'key':
                    confirm = input(f"Use {found.get('name')} (this will consume it)? (y/n) ").lower().strip()
                    if confirm != 'y':
                        print('Cancelled.')
                        continue
                used = player.use_item(found, world, ship, pm)
                if used:
                    print(f"You used {found.get('name')}.")
                    # rebuild ship if world changed
                    ship = Ship(world.map, world.items)
                else:
                    print("You can't use that here.")

        elif cmd.startswith("solve "):
            puzzle_id = cmd.split(" ", 1)[1].strip()
            pm.attempt_puzzle(puzzle_id, player, world)
            # Persist puzzle state back to world for saving
            try:
                world.puzzles = list(pm.puzzles.values())
            except Exception:
                world.puzzles = pm.puzzles
            # Rebuild ship if puzzle changed the map/items
            ship = Ship(world.map, world.items)

        elif cmd.startswith("drop "):
            item_id = cmd.split(" ", 1)[1].strip()
            # confirm before dropping
            confirm = input(f"Drop {item_id}? (y/n) ").lower().strip()
            if confirm != 'y':
                print("Drop cancelled.")
            else:
                ok = player.drop_item(item_id, world)
                if ok:
                    print(f"Dropped {item_id} into storage.")
                else:
                    print("No storage here or item not found.")

        elif cmd.startswith("take "):
            item_id = cmd.split(" ", 1)[1].strip()
            ok = player.take_from_storage(item_id, world)
            if ok:
                print(f"Took {item_id} from storage.")
            else:
                print("Nothing to take or inventory full.")

        elif cmd == "look":
            # describe current tile
            room = ship.current_room(player.position)
            print(f"You are at {player.position} in {room}.")
            # items on ground
            ground = [it for it in world.items if it.get("position") and tuple(it.get("position")) == player.position]
            if ground:
                print("On the ground:")
                for g in ground:
                    print(f" - {g.get('name')} ({g.get('id')})")
            # storage here?
            storage = [s for s in world.items if s.get("type") == "storage" and tuple(s.get("position")) == player.position]
            if storage:
                print("Storage here:")
                for s in storage:
                    print(f" - {s.get('name')}")
                    contents = s.get('contents', [])
                    if not contents:
                        print("    (empty)")
                    else:
                        for c in contents:
                            qty = c.get('quantity', 1)
                            print(f"    - {c.get('name')} ({c.get('id')}) x{qty}")
            # enemies in room
            enemies = [e for e in world.enemies if e.get("location") and tuple(e.get("location")) == player.position and e.get("alive", True)]
            if enemies:
                print("Enemies here:")
                for e in enemies:
                    print(f" - {e.get('name')}")

        elif cmd.startswith("inspect "):
            item_id = cmd.split(" ", 1)[1].strip()
            # check inventory
            it = next((i for i in player.inventory if i.get("id") == item_id or i.get("name", "").lower() == item_id.lower()), None)
            if it:
                print(it.get("description", "No description."))
                continue
            # check ground
            it = next((i for i in world.items if (i.get("position") and tuple(i.get("position")) == player.position) and (i.get("id") == item_id or i.get("name", "").lower() == item_id.lower())), None)
            if it:
                print(it.get("description", "No description."))
                continue
            # check storage
            st = next((s for s in world.items if s.get("type") == "storage" and tuple(s.get("position")) == player.position), None)
            if st:
                cont = next((c for c in st.get("contents", []) if c.get("id") == item_id), None)
                if cont:
                    print(cont.get("name", "") + ": " + str(cont.get("quantity", 1)))
                    continue
            print("Item not found here.")

        elif cmd == "save":
            save_game(player, world)

        elif cmd == "load":
            ok = load_game(player, world)
            if ok:
                # rebuild ship after loading world state
                ship = Ship(world.map, world.items)
                # refresh puzzle manager state as well
                pm = PuzzleManager(WORLD)
                if getattr(world, "puzzles", None):
                    if isinstance(world.puzzles, list):
                        pm.puzzles = {p["id"]: p for p in world.puzzles}
                    elif isinstance(world.puzzles, dict):
                        pm.puzzles = world.puzzles

        elif cmd == "quit":
            print("Exiting game.")
            break

        else:
            print("Unknown command. Type 'help' for commands.")

if __name__ == "__main__":
    main()
