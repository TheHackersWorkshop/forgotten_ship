import os
import json
from src.inventory import Item

SAVEGAME_FILE = "data/savegame.json"
SETTINGS_FILE = "data/settings.json"
ASCII_ART_FILE = os.path.join("data", "art", "ascii_art.json")

_ascii_art_cache = {}  # Holds loaded ASCII art entries

def load_settings():
    """Load game settings from the settings.json file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_game(player):
    """Save the player's game state to a JSON file."""
    save_data = {
        "player": {
            "name": player.name,
            "position": list(player.position),  # e.g., ['J', 10]
            "health": player.health,
            "inventory": [
                {"name": item.name, "category": item.category, "description": item.description}
                for item in player.inventory
            ],
            "explored_coords": [list(coord) for coord in player.explored_coords]
        },
        "doors": [list(door) for door in player.doors_coords.keys()]
    }

    try:
        with open(SAVEGAME_FILE, "w") as f:
            json.dump(save_data, f, indent=4)
        print("Game saved successfully!")
    except IOError as e:
        print(f"Error saving game: {e}")


def load_game():
    """Load the player's game state from a JSON file."""
    if os.path.exists(SAVEGAME_FILE):
        try:
            with open(SAVEGAME_FILE, "r") as f:
                save_data = json.load(f)

            player_data = save_data["player"]
            position = tuple(player_data["position"])
            health = player_data["health"]
            inventory = [Item(item["name"], item["category"], item["description"]) for item in player_data["inventory"]]
            explored_coords = {tuple(coord) for coord in player_data["explored_coords"]}
            doors_coords = {tuple(door): tuple(door) for door in save_data.get("doors", [])}

            return position, health, inventory, explored_coords, doors_coords

        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading savegame: {e}")
            return None, None, [], set(), {}
    else:
        print("No saved game found.")
        return None, None, [], set(), {}


def generate_map(player_position, doors_coords):
    """
    Display the ship's map with the current player's position,
    explored areas (from visited_coords in settings), and visible doors.
    """
    width, height = 26, 25  # A-Z (26 columns), 1–25 rows
    ship_map = [[" " for _ in range(width)] for _ in range(height)]
    cols = [chr(i) for i in range(ord('A'), ord('Z') + 1)]

    # Load visited_coords from settings.json
    settings = load_settings()
    visited_coords = {tuple(coord) for coord in settings.get("visited_coords", [])}

    # Plot visited cells
    for col_letter, row_num in visited_coords:
        x = cols.index(col_letter.upper())
        y = row_num - 1
        ship_map[y][x] = 'o'

    # Plot doors in visited areas only
    for coord in doors_coords.values():
        col_letter, row_num = coord
        if (col_letter, row_num) in visited_coords:
            x = cols.index(col_letter.upper())
            y = row_num - 1
            ship_map[y][x] = 'D'

    # Plot player
    px_letter, py_num = player_position
    px = cols.index(px_letter.upper())
    py = py_num - 1
    ship_map[py][px] = '@'

    # Print map from top (25) to bottom (1)
    print("\n=== SHIP MAP ===")
    for y in reversed(range(height)):
        row_label = f"{y + 1:2}"
        row_data = "".join(ship_map[y])
        print(f"{row_label} | {row_data}")

    header = "     " + "  ".join(cols)
    print(header)


# === ASCII ART SECTION ===

def load_ascii_art():
    """Load ASCII art data from a JSON file into memory once."""
    global _ascii_art_cache
    if not _ascii_art_cache:
        if os.path.exists(ASCII_ART_FILE):
            try:
                with open(ASCII_ART_FILE, "r") as f:
                    _ascii_art_cache = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error loading ASCII art: {e}")
        else:
            print("Warning: ASCII art file not found.")
    return _ascii_art_cache


def show_ascii_art(art_id):
    """
    Display ASCII art and description based on art ID.

    Parameters:
        art_id (str): The numeric key of the art to show, e.g., "01"
    """
    art_data = load_ascii_art().get(art_id)

    if art_data:
        print()  # Spacer line before art
        for line in art_data["art"]:
            print(line)
        if "description" in art_data:
            print(f"\n{art_data['description']}")
    else:
        print(f"[Missing ASCII art for ID {art_id}]")
