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

def save_item_positions_to_settings(item_positions, visited_coords=None, completed_tasks=None):
    """Save the randomly generated item positions and additional player state to settings.json."""
    settings_data = {
        "item_positions": item_positions,
    }

    # NEW: Add visited_coords and completed_tasks
    if visited_coords is not None:
        settings_data["visited_coords"] = visited_coords
    if completed_tasks is not None:
        settings_data["completed_tasks"] = completed_tasks

    with open(SETTINGS_FILE, 'w') as settings_file:
        json.dump(settings_data, settings_file, indent=4)


def load_logs(filepath="data/logs.json"):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return {}
    with open(filepath, "r") as f:
        return json.load(f)

def save_game(player):
    """Save the current game state to file."""
    save_data = {
        "position": player.position,
        "inventory": [item.name for item in player.inventory],
        "room_items": {
            room: [item.name for item in data.get("compartment", [])]
            for room, data in SHIP_MAP.items()
        }
    }

    # Save magic storage if available
    if hasattr(player, "magic_storage"):
        save_data["magic_storage"] = {
            box: [item.name for item in items]
            for box, items in player.magic_storage.items()
        }

    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f, indent=4)
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

        # Initialize magic_storage even if empty
        player.magic_storage = {}

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

        # Restore magic_storage if present
        for box_name, items in save_data.get("magic_storage", {}).items():
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
    """Load the item positions and player state from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as settings_file:
            settings_data = json.load(settings_file)
            return {
                "item_positions": settings_data.get("item_positions", {}),
                "visited_coords": settings_data.get("visited_coords", []),
                "completed_tasks": settings_data.get("completed_tasks", []),
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "item_positions": {},
            "visited_coords": [],
            "completed_tasks": [],
        }


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
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Left, Right, Up, Down

    for dx, dy in directions:
        new_x_index = x_index + dx
        new_y_index = y_index + dy

        # Ensure the new coordinates are within bounds (you can adjust the bounds as needed)
        if 0 <= new_x_index < 10 and 0 <= new_y_index < 10:  # Assuming 10x10 grid
            # Convert back the x_index to a letter
            new_x = chr(new_x_index + ord('A'))
            new_y = new_y_index + 1  # Convert back to 1-based y-coordinate
            visible.append((new_x, new_y))

    return visible

def get_room_dialogue(room_name, log_data):
    key = room_name.lower().replace(" ", "_")
    room_info = log_data.get("rooms", {}).get(key, {})
    description = room_info.get("description", "No description available.")
    dialogue = room_info.get("dialogue", [])
    return description, dialogue

def process_room_dialogue(player, room_name, dialogue_data):
    """Display the first valid dialogue line based on triggers, flags, and repetition rules."""
    character_dialogue = dialogue_data.get(player.name.lower(), {})
    room_dialogues = character_dialogue.get(room_name, [])

    for line in room_dialogues:
        trigger = line.get("trigger")
        flag = line.get("flag")
        repeatable = line.get("repeatable", False)

        if trigger and trigger not in player.completed_tasks:
            continue

        if flag and flag in player.dialogue_flags and not repeatable:
            continue

        print(f"{player.name}: {line['line']}")

        if flag:
            player.dialogue_flags[flag] = True

        break  # Only process one line per visit


def trigger_dialogue_by_id(player, dialogue_data, dialogue_id):
    """Manually trigger a specific dialogue line by its unique ID."""
    character_dialogue = dialogue_data.get(player.name.lower(), {})

    for room_dialogues in character_dialogue.values():
        for line in room_dialogues:
            if line.get("id") == dialogue_id:
                print(f"{player.name}: {line['line']}")
                flag = line.get("flag")
                if flag:
                    player.dialogue_flags[flag] = True
                return True  # Dialogue was found and triggered
    return False  # No matching dialogue found

def main():
    dialogue_data = load_dialogue()         # character-specific dialogue (Ryan, Rachel)
    log_data = load_logs()                  # intro, ship logs, room descriptions, alarms

    player = load_game()

    # Load from settings
    settings = load_item_positions()
    item_positions = settings["item_positions"]
    player.visited_coords = settings["visited_coords"]
    player.completed_tasks = settings["completed_tasks"]

    # If no positions were previously saved, generate them
    if not item_positions:
        item_positions = generate_item_placement()
        save_item_positions_to_settings(item_positions, player.visited_coords, player.completed_tasks)

    print("Welcome to Forgotten Ship.")
    print(log_data.get('intro', "Intro text not found."))
    print("Type 'help' for available commands.\n")

    while player.is_alive():
        room_name, room_data = get_room(player.position)

        if not room_data:
            print(f"You are floating in space. No room found at {player.position}.")
            break

        description, room_dialogue = get_room_dialogue(room_name, log_data)
        item_positions = load_item_positions()

        # --- NEW: Field-of-view item filtering ---
        visible_items = {}
        if room_name == player.get_current_room_name():
            visible_items = item_positions.get(room_name, {})
        else:
            visible_coords = get_visible_coords(player.position, flashlight_on=player.has_flashlight)
            room_items = item_positions.get(room_name, {})
            visible_items = {
                name: pos for name, pos in room_items.items() if pos in visible_coords
            }

        # Show ASCII art on entry conditionally
        if random.random() < 0.2:
            show_ascii_art("01")

        print(f"\nYou are in: {room_name}")
        print(f"Description: {description}")
        if visible_items:
            print(f"Items found: {', '.join(visible_items.keys())}")
            print(f"Compartment contains: {', '.join([item.name for item in room_data['compartment']])}")
        if room_dialogue:
            print("Dialogue:")
            for line in room_dialogue:
                print(f"- {line}")

        command = input("\nEnter command: ").strip().lower()

        if command == "look":
            current_room = player.get_current_room()
            print(f"\nYou look around the room. {current_room['description']}")
            if current_room.get("items"):
                print(f"Items found: {', '.join(current_room['items'])}")
            if 'exits' in current_room:
                print(f"Exits: {', '.join(current_room.get('exits', []))}")
            if current_room.get("compartment"):
                print(f"Compartment contains: {', '.join(current_room['compartment'])}")
            if room_dialogue:
                print(f"Dialogue: {', '.join(room_dialogue)}")

        elif command.startswith("move "):
            parts = command.split()
            if len(parts) == 2:
                direction = parts[1]
                player.move(direction)
                room_name, _ = get_room(player.position)
                from src.puzzles import check_puzzle_trigger
                check_puzzle_trigger(player, "move", room_name)
                save_item_positions_to_settings(item_positions, player.visited_coords, player.completed_tasks)
            elif len(parts) == 3:
                direction = parts[1]
                try:
                    steps = int(parts[2])
                    player.move(direction, steps)
                    room_name, _ = get_room(player.position)
                    from src.puzzles import check_puzzle_trigger
                    check_puzzle_trigger(player, "move", room_name)
                except ValueError:
                    print("Invalid number of steps. Please enter a valid integer.")
            else:
                print("Invalid command. Usage: move [direction] [steps]")

        elif command == "inventory":
            player.list_inventory()

        elif command == "use door":
            player.use_door()

        elif command == "status":
            player.status()

        elif command == "reset":
            confirm = input("Are you sure you want to reset the game? (yes/no): ").strip().lower()
            if confirm == "yes":
        # --- Reset savegame.json ---
                blank_save = {
                    "position": ["I", 5],
                    "inventory": [],
                    "magic_storage": {},
                    "room_items": {
                        room: [] for room in [
                            "Bridge", "Server Room", "Weapons Room", "Engine Room", "Airlock", "Corridor",
                            "Cargo Bay (Start)", "Sleeping Quarters 1", "Sleeping Quarters 2",
                            "Sleeping Quarters 3", "Sleeping Quarters 4", "Chow Hall", "Med Bay",
                            "Secret Passage 1", "Secret Passage 2", "Secret Passage 3"
                        ]
                    }
                }
                with open("data/savegame.json", "w") as f:
                    json.dump(blank_save, f, indent=2)
                print("Player savegame has been cleared.")

        # --- Reset settings.json ---
                def generate_random_settings():
                    room_names = list(blank_save["room_items"].keys())
                    item_names = list(ITEM_CATALOG.keys())

            # Example random distribution of items
                    shuffled_items = random.sample(item_names, min(10, len(item_names)))
                    placed_items = {
                        room: [] for room in room_names
                    }
                    for item in shuffled_items:
                        room_choice = random.choice(room_names)
                        placed_items[room_choice].append(item)

                    return {
                        "visited_coords": [],
                        "completed_tasks": [],
                        "played_puzzles": [],
                        "dialogue_flags": {},
                        "item_positions": placed_items
                    }

                new_settings = generate_random_settings()
                with open("data/settings.json", "w") as f:
                    json.dump(new_settings, f, indent=2)
                print("Game settings (world state) have been reset.")

        # --- Reinitialize player object in fresh state ---
                player = load_game()
                print("\nGame has been fully reset.\n")
                player.update_room()

        elif command.startswith("store "):
            item_name = command.replace("store ", "").strip()
            player.store_item_in_magic_box(item_name)

        elif command.startswith("drop "):
            item_name = command.replace("drop ", "").strip()
            player.drop_item(item_name)

        elif command == "solve puzzle":
            puzzle, category, index = get_random_puzzle(puzzles)

            if is_puzzle_solved(category, index):
                print("You’ve already solved this puzzle.")
            else:
                print(f"Solve the puzzle: {puzzle['question']}")
                player_input = input("Your answer: ").strip().lower()

                if is_correct_answer(puzzle, player_input):
                    print("Correct! You unlocked new content.")
                    mark_puzzle_solved(category, index)

                    puzzle_tag = f"{category}_{index}"
                    unlock_related_content(puzzle_tag)

                    if puzzle.get('unlock_log'):
                        log = puzzle['unlock_log']
                        print(f"Log Unlocked: {log['title']}")
                        print(log['content'])

                    if puzzle.get('unlock_dialogue'):
                        print(f"New Dialogue: {puzzle['unlock_dialogue']}")
                else:
                    print("Incorrect. Try again.")

        elif command == "save":
            save_game(player)

        elif command == "quit":
            print("Saving and exiting game...")
            save_game(player)
            break

        elif command.startswith("use "):
            item_name = command.replace("use ", "").strip()
            player.use_item(item_name)
            from src.puzzles import check_puzzle_trigger
            check_puzzle_trigger(player, "use_item", item_name)

        elif command == "map":
            display_map(player)

        elif command == "help":
            print("Available commands:")
            print(" - look")
            print(" - move [direction] [steps] (e.g., move bow 3)")
            print(" - use [item name]")
            print(" - store [item name]")
            print(" - drop [item name]")
            print(" - use door")
            print(" - inventory")
            print(" - status")
            print(" - solve puzzle")
            print(" - save")
            print(" - quit")
            print(" - reset")
            print(" - map")

        else:
            print("Invalid command. Type 'help' for options.")


if __name__ == "__main__":
    main()
