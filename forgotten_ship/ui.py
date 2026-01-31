import json
import os

SAVE_FILE = "savegame.json"

def render_map(ship, player, items=None):
    cols = [chr(i) for i in range(65, 91)]
    width, height = 26, 25
    grid = [[" "]*width for _ in range(height)]

    visible = player.visible_tiles(ship)

    for col, row in player.visited:
        if col in cols and 1 <= row <= height:
            grid[row-1][cols.index(col)] = "."

    for pos in ship.doors:
        if pos in visible:
            col, row = pos
            if col in cols and 1 <= row <= height:
                grid[row-1][cols.index(col)] = "D"

    if items:
        for item in items:
            if item.get("position"):
                pos = tuple(item["position"])
                if pos in visible:
                    col, row = pos
                    if col in cols and 1 <= row <= height:
                        grid[row-1][cols.index(col)] = "I"

    pcol, prow = player.position
    if pcol in cols and 1 <= prow <= height:
        grid[prow-1][cols.index(pcol)] = "P"

    print("\n=== SHIP MAP ===")
    for y in range(height-1, -1, -1):
        print(f"{y+1:2} | {''.join(grid[y])}")
    print("    " + " ".join(cols))

def show_dialogue(entry):
    if not entry:
        return
    prefix = {"thought": "(Ryan thinks)", "log": "[SYSTEM LOG]"}.get(entry["type"], "")
    print(f"\n{prefix} {entry['line']}\n")

def show_help():
    print("\nCommands:")
    print(" n - move north")
    print(" s - move south")
    print(" e - move east")
    print(" w - move west")
    print(" inventory - show inventory")
    print(" use <item> - use an item (e.g., 'use flashlight' or 'use medkit')")
    print(" drop <item> - drop an item into nearby storage (must be at a storage location)")
    print(" take <item> - take an item from nearby storage (must be at a storage location)")
    print(" look - inspect current location (items, storage, enemies)")
    print(" inspect <item> - show item description if available")
    print(" solve <puzzle_id> - attempt to solve a puzzle (if present)")
    print(" save - save game")
    print(" load - load game")
    print(" quit - quit game\n")

def save_game(player, world):
    data = {
        "player": {
            "position": player.position,
            "health": player.health,
            "flashlight": player.flashlight,
            "visited": list(player.visited),
            "inventory": player.inventory
        },
        "world": {
            "items": world.items,
            "enemies": world.enemies,
            "puzzles": world.puzzles,
            "logs": world.logs,
            "stage": getattr(world, "stage", 0)
        }
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("Game saved.")

def load_game(player, world):
    if not os.path.exists(SAVE_FILE):
        print("No save file found.")
        return False
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)

    p = data["player"]
    player.position = tuple(p["position"])
    player.health = p["health"]
    player.flashlight = p["flashlight"]
    player.visited = set(tuple(pos) for pos in p["visited"])
    player.inventory = p.get("inventory", [])

    w = data["world"]
    world.items = w["items"]
    world.enemies = w["enemies"]
    world.puzzles = w["puzzles"]
    world.logs = w["logs"]
    world.stage = w.get("stage", 0)

    print("Game loaded.")
    return True
