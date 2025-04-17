import json
import os
import random
from src.ship import get_room, get_room_dialogue, load_dialogue, SHIP_MAP
from src.player import Player
from src.inventory import ITEM_CATALOG
from src.puzzles import load_puzzles, get_random_puzzle, is_correct_answer
from src.ui import generate_map, show_ascii_art  # <-- new import

SAVE_FILE = 'data/savegame.json'
SETTINGS_FILE = 'data/settings.json'
puzzles = load_puzzles()


def generate_item_placement():
    """Logically and randomly place items in valid ship rooms with constraints."""
    item_positions = {}

    # Extract valid rooms with coordinates
    valid_rooms = {
        room: data.get("coords", [])
        for room, data in SHIP_MAP.items()
        if data.get("coords")
    }

    # Build a dynamic restriction map for keys: which room they unlock
    key_unlocks_room = {}
    for item_name, item in ITEM_CATALOG.items():
        if item.category == "key":
            for room in SHIP_MAP:
                if SHIP_MAP[room].get("locked"):
                    # Match "Room 1 Key" to "Sleeping Quarters 1", "Bridge Key" to "Bridge", etc.
                    if item_name.lower().startswith(room.lower().split()[0].lower()):
                        key_unlocks_room[item_name] = room
                        break
                    elif item_name.lower().replace(" key", "") in room.lower():
                        key_unlocks_room[item_name] = room
                        break

    # Shuffle room list to aid distribution
    shuffled_rooms = list(valid_rooms.keys())
    random.shuffle(shuffled_rooms)

    for item_name, item_obj in ITEM_CATALOG.items():
        restricted_room = key_unlocks_room.get(item_name)

        eligible_rooms = [
            room for room in shuffled_rooms
            if room != restricted_room and valid_rooms[room]
        ]

        if not eligible_rooms:
            print(f"[Warning] No eligible rooms found for item '{item_name}'. Skipping.")
            continue

        selected_room = random.choice(eligible_rooms)
        selected_coord = random.choice(valid_rooms[selected_room])

        if selected_room not in item_positions:
            item_positions[selected_room] = {}

        item_positions[selected_room][item_name] = selected_coord

    return item_positions


def store_item_in_magic_box(self, item_name):
    item = self.get_item_from_inventory(item_name)
    if not item:
        print(f"Item '{item_name}' not found in your inventory.")
        return

    box_name = input("Enter the magic box name: ")
    if box_name not in self.magic_storage:
        self.magic_storage[box_name] = []

    self.magic_storage[box_name].append(item)
    self.inventory.remove(item)
    print(f"You stored {item_name} in the magic box '{box_name}'.")


# Function for dropping items
def drop_item(self, item_name):
    item = self.get_item_from_inventory(item_name)
    if not item:
        print(f"Item '{item_name}' not found in your inventory.")
        return
    self.inventory.remove(item)
    print(f"You dropped {item_name}.")


def save_item_positions_to_settings(item_positions):
    """Save the randomly generated item positions to settings.json."""
    settings_data = {
        "item_positions": item_positions,
    }
    with open(SETTINGS_FILE, 'w') as settings_file:
        json.dump(settings_data, settings_file, indent=4)


def save_game(player):
    """Save the current game state to file."""
    save_data = {
        "position": player.position,
        "inventory": [item.name for item in player.inventory],
        "room_items": {
            room: data.get("compartment", []) for room, data in SHIP_MAP.items()
        }
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f)
    print("Game saved.")


def load_game():
    """Load the game state from file or start a new game if invalid."""
    if not os.path.exists(SAVE_FILE):
        print("No save game found. Starting new game.")
        return Player()

    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)

        if "position" not in save_data or "inventory" not in save_data:
            raise KeyError("Save file is missing required data. Starting new game.")

        player = Player(position=tuple(save_data["position"]))

        def get_item_by_name(item_entry):
            if isinstance(item_entry, dict):
                name = item_entry.get("name")
                return ITEM_CATALOG.get(name)
            elif isinstance(item_entry, str):
                return ITEM_CATALOG.get(item_entry)
            return None

        for item_entry in save_data["inventory"]:
            item_obj = get_item_by_name(item_entry)
            if item_obj:
                player.inventory.append(item_obj)

        if hasattr(player, "magic_storage") and "magic_storage" in save_data:
            for box_name, items in save_data["magic_storage"].items():
                player.magic_storage[box_name] = []
                for item_entry in items:
                    item_obj = get_item_by_name(item_entry)
                    if item_obj:
                        player.magic_storage[box_name].append(item_obj)

        for room, item_list in save_data.get("room_items", {}).items():
            SHIP_MAP[room]["compartment"] = []
            for item_entry in item_list:
                item_obj = get_item_by_name(item_entry)
                if item_obj:
                    SHIP_MAP[room]["compartment"].append(item_obj)

        print("Game loaded.")
        return player

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error loading save file: {e}")
        print("Starting a new game instead.")
        return Player()


def load_item_positions():
    """Load the item positions from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as settings_file:
            settings_data = json.load(settings_file)
            return settings_data.get("item_positions", {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def display_map(player):
    """Display the map of the ship to help the player navigate."""
    generate_map(player.position, player.explored_coords, player.doors_coords)


def get_visible_coords(position, flashlight_on=False):
    x, y = position
    visible = []

    # Convert x (a letter) to its index (A = 0, B = 1, etc.)
    x_index = ord(x) - ord('A')  # A becomes 0, B becomes 1, and so on
    y_index = y - 1  # Convert y to a 0-based index

    # Define possible directions (dx, dy)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # left, right, down, up

    for dx, dy in directions:
        new_x = x_index + dx
        new_y = y_index + dy

        if 0 <= new_x < len(SHIP_MAP) and 0 <= new_y < len(SHIP_MAP[0]):
            visible.append((chr(new_x + ord('A')), new_y + 1))  # Convert back to letter and 1-based index

    if flashlight_on:
        # Add a wider area or special tiles if the flashlight is on
        pass  # You can add logic for flashlight effect here.

    return visible


def play_game():
    """Main game loop."""
    player = load_game()  # Load the saved game or start fresh.
    item_positions = load_item_positions()

    print("Welcome to the Forgotten Ship.")

    while True:
        display_map(player)
        print(f"You're in {get_room(player.position)}.")
        action = input("What do you want to do? ")

        if action == "quit":
            save_game(player)
            print("Goodbye!")
            break
        elif action == "explore":
            visible_coords = get_visible_coords(player.position, flashlight_on=True)
            print("You see the following places:")
            for coord in visible_coords:
                print(f"  {coord}")
        elif action == "check inventory":
            print("Your inventory contains:")
            for item in player.inventory:
                print(f"  {item.name}")
        # Add other actions as needed

if __name__ == "__main__":
    play_game()
