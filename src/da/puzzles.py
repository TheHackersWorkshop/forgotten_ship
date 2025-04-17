import json
import random
import difflib
import os

PUZZLE_FILE = "data/puzzles.json"
LOG_FILE = "data/logs.json"
DIALOGUE_FILE = "data/dialogue.json"
PUZZLE_STATE_FILE = "data/puzzle_state.json"

def load_puzzles():
    """Loads puzzles from the file."""
    if not os.path.exists(PUZZLE_FILE):
        return {}
    try:
        with open(PUZZLE_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding {PUZZLE_FILE}. Returning empty puzzles.")
        return {}

def load_logs():
    """Loads logs from the file."""
    if not os.path.exists(LOG_FILE):
        return {}
    try:
        with open(LOG_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding {LOG_FILE}. Returning empty logs.")
        return {}

def save_logs(logs):
    """Saves logs to the file."""
    try:
        with open(LOG_FILE, "w") as file:
            json.dump(logs, file, indent=4)
    except IOError:
        print(f"Error writing to {LOG_FILE}.")

def load_dialogue():
    """Loads dialogue from the file."""
    if not os.path.exists(DIALOGUE_FILE):
        return {}
    try:
        with open(DIALOGUE_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Error decoding {DIALOGUE_FILE}. Returning empty dialogue.")
        return {}

def save_dialogue(dialogue):
    """Saves dialogue to the file."""
    try:
        with open(DIALOGUE_FILE, "w") as file:
            json.dump(dialogue, file, indent=4)
    except IOError:
        print(f"Error writing to {DIALOGUE_FILE}.")

def load_puzzle_state():
    """Loads puzzle state tracking."""
    if os.path.exists(PUZZLE_STATE_FILE):
        try:
            with open(PUZZLE_STATE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding {PUZZLE_STATE_FILE}. Returning empty puzzle state.")
    return {}

def save_puzzle_state(state):
    """Saves puzzle state tracking."""
    try:
        with open(PUZZLE_STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except IOError:
        print(f"Error writing to {PUZZLE_STATE_FILE}.")

def get_random_puzzle(puzzles, category=None):
    """Returns a random puzzle, optionally from a specific category."""
    if category:
        index = random.randint(0, len(puzzles[category]) - 1)
        return puzzles[category][index], category, index
    else:
        all = []
        for cat in puzzles:
            for i, p in enumerate(puzzles[cat]):
                all.append((p, cat, i))
        return random.choice(all)

def is_correct_answer(puzzle, player_input):
    """Checks if the player's answer is correct."""
    normalized_input = player_input.strip().lower()

    if puzzle['type'] == "riddle":
        for answer in puzzle['answers']:
            similarity = difflib.SequenceMatcher(None, normalized_input, answer.lower()).ratio()
            if similarity > 0.75 or normalized_input in answer.lower():
                return True
        return False

    elif puzzle['type'] in ("logic", "cipher"):
        return normalized_input == puzzle['answer'].strip().lower()

    else:
        print(f"Unknown puzzle type: {puzzle['type']}")
        return False

def mark_puzzle_solved(category, index):
    """Marks a puzzle as solved and updates the puzzle state."""
    state = load_puzzle_state()
    puzzle_key = f"{category}_{index}"
    if puzzle_key in state:
        print(f"Puzzle {puzzle_key} already solved.")
        return False
    state[puzzle_key] = True
    save_puzzle_state(state)
    print(f"Marked puzzle {puzzle_key} as solved.")
    return True

def is_puzzle_solved(category, index):
    """Checks if a puzzle has already been solved."""
    state = load_puzzle_state()
    return state.get(f"{category}_{index}", False)

def unlock_related_content(puzzle_tag):
    """Unlocks content based on the puzzle tag."""
    logs = load_logs()
    dialogue = load_dialogue()

    if puzzle_tag == "logic_0":
        logs["log_002"]["unlocked"] = True
        print("Unlocked log_002: Power Restored")

        new_line = "Rachel: Power is flowing again. Systems are responding."
        if "rooms" in dialogue and "engine_room" in dialogue["rooms"]:
            dialogue["rooms"]["engine_room"]["dialogue"].append(new_line)

        save_logs(logs)
        save_dialogue(dialogue)
