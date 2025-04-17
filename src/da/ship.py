# Manages ship structure
import json

# Load dialogue.json file (external)
def load_dialogue():
    """Loads the dialogue data from the dialogue.json file."""
    try:
        with open('data/dialogue.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Dialogue file not found.")
        return {}

def get_room_dialogue(room_name, dialogue_data):
    """Fetches the dialogue and description for the given room."""
    room_data = dialogue_data.get(room_name, {})
    description = room_data.get("description", "No description available.")
    dialogue = room_data.get("dialogue", [])
    return description, dialogue

SHIP_MAP = {
    "Bridge": {
        "coords": [("I", 19), ("J", 19), ("K", 19), ("L", 19),
                   ("I", 20), ("J", 20), ("K", 20), ("L", 20),
                   ("I", 21), ("J", 21), ("K", 21), ("L", 21),
                   ("I", 22), ("J", 22), ("K", 22), ("L", 22)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "The nerve center of the ship, filled with blinking consoles and control panels.",
        "doors": {
            "to corridor": {
                "entry": ("K", 22),
                "exit": ("K", 23),
                "locked": False
            }
        },
        "secret_passages": {
            "to engine room": {
                "entry": ("I", 19),
                "exit": ("F", 19),
                "revealed": False
            }
        }
    },

    "Server Room": {
        "coords": [("M", 19), ("N", 19), ("O", 19),
                   ("M", 20), ("N", 20), ("O", 20),
                   ("M", 21), ("N", 21), ("O", 21)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "A room packed with humming servers and backup data systems.",
        "doors": {}
    },

    "Weapons Room": {
        "coords": [("P", 19), ("Q", 19),
                   ("P", 20), ("Q", 20)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "A secure armory lined with weapon storage lockers.",
        "doors": {}
    },

    "Engine Room": {
        "coords": [("C", 5), ("D", 5), ("E", 5), ("F", 5), ("G", 5), ("H", 5),
                   ("C", 6), ("D", 6), ("E", 6), ("F", 6), ("G", 6), ("H", 6),
                   ("C", 7), ("D", 7), ("E", 7), ("F", 7), ("G", 7), ("H", 7)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "The ship’s propulsion systems rumble here, shrouded in heat and steam.",
        "doors": {}
    },

    "Airlock": {
        "coords": [("I", 3), ("J", 3),
                   ("I", 4), ("J", 4)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "A decompression chamber leading out into the cold void of space.",
        "doors": {}
    },

    "Corridor": {
        "coords": [("I", 10), ("J", 10), ("K", 10), ("L", 10),
                   ("I", 11), ("J", 11), ("K", 11), ("L", 11),
                   ("I", 12), ("J", 12), ("K", 12), ("L", 12),
                   ("I", 13), ("J", 13), ("K", 13), ("L", 13),
                   ("I", 14), ("J", 14), ("K", 14), ("L", 14),
                   ("I", 15), ("J", 15), ("K", 15), ("L", 15),
                   ("I", 16), ("J", 16), ("K", 16), ("L", 16), ("M", 16), ("N", 16), ("O", 16), ("P", 16), ("Q", 16), ("R", 16), ("S", 16), ("T", 16),
                   ("I", 17), ("J", 17), ("K", 17), ("L", 17), ("M", 17), ("N", 17), ("O", 17), ("P", 17), ("Q", 17), ("R", 17), ("S", 17), ("T", 17),
                   ("I", 18), ("J", 18), ("K", 18), ("L", 18), ("M", 18), ("N", 18), ("O", 18), ("P", 18), ("Q", 18), ("R", 18), ("S", 18), ("T", 18),
                   ("R", 19), ("S", 19), ("T", 19),
                   ("R", 20), ("S", 20), ("T", 20),
                   ("P", 21), ("Q", 21), ("R", 21), ("S", 21), ("T", 21),
                   ("M", 22), ("N", 22), ("O", 22), ("P", 22), ("Q", 22), ("R", 22), ("S", 22), ("T", 22),
                   ("I", 23), ("J", 23), ("K", 23), ("L", 23), ("M", 23), ("N", 23), ("O", 23), ("P", 23), ("Q", 23), ("R", 23), ("S", 23), ("T", 23),
                   ("I", 24), ("J", 24), ("K", 24), ("L", 24), ("M", 24), ("N", 24), ("O", 24), ("P", 24), ("Q", 24), ("R", 24), ("S", 24), ("T", 24)],
        "locked": False,
        "key": None,
        "items": [],
        "description": "A long stretch of corridor connecting the various rooms of the ship.",
        "doors": {}
    },

    "Cargo Bay (Start)": {
        "coords": [("I", 5), ("J", 5), ("K", 5), ("L", 5), ("M", 5), ("N", 5), ("O", 5), ("P", 5), ("Q", 5),
                   ("I", 6), ("J", 6), ("K", 6), ("L", 6), ("M", 6), ("N", 6), ("O", 6), ("P", 6), ("Q", 6),
                   ("I", 7), ("J", 7), ("K", 7), ("L", 7), ("M", 7), ("N", 7), ("O", 7), ("P", 7), ("Q", 7),
                   ("C", 8), ("D", 8), ("E", 8), ("F", 8), ("G", 8), ("H", 8), ("I", 8), ("J", 8), ("K", 8), ("L", 8), ("M", 8), ("N", 8), ("O", 8), ("P", 8), ("Q", 8),
                   ("C", 9), ("D", 9), ("E", 9), ("F", 9), ("G", 9), ("H", 9), ("I", 9), ("J", 9), ("K", 9), ("L", 9), ("M", 9), ("N", 9), ("O", 9), ("P", 9), ("Q", 9)],
        "locked": False,
        "key": None,
        "items": [],
        "description": "Large and open, filled with crates and equipment. Your journey begins here.",
        "doors": {}
    },

    "Sleeping Quarters 1": {
        "coords": [("C", 10), ("D", 10), ("E", 10), ("F", 10), ("G", 10), ("H", 10),
                   ("C", 11), ("D", 11), ("E", 11), ("F", 11), ("G", 11), ("H", 11),
                   ("C", 12), ("D", 12), ("E", 12), ("F", 12), ("G", 12), ("H", 12)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "A compact crew sleeping area with bunk beds and footlockers.",
        "doors": {}
    },

    "Sleeping Quarters 2": {
        "coords": [("M", 10), ("N", 10), ("O", 10), ("P", 10), ("Q", 10),
                   ("M", 11), ("N", 11), ("O", 11), ("P", 11), ("Q", 11),
                   ("M", 12), ("N", 12), ("O", 12), ("P", 12), ("Q", 12)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "Neatly arranged beds and dim lights offer the crew some rest here.",
        "doors": {}
    },

    "Sleeping Quarters 3": {
        "coords": [("C", 13), ("D", 13), ("E", 13), ("F", 13), ("G", 13), ("H", 13),
                   ("C", 14), ("D", 14), ("E", 14), ("F", 14), ("G", 14), ("H", 14),
                   ("C", 15), ("D", 15), ("E", 15), ("F", 15), ("G", 15), ("H", 15)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "An auxiliary sleeping area for emergency or overflow crew.",
        "doors": {}
    },

    "Sleeping Quarters 4": {
        "coords": [("M", 13), ("N", 13), ("O", 13), ("P", 13), ("Q", 13),
                   ("M", 14), ("N", 14), ("O", 14), ("P", 14), ("Q", 14),
                   ("M", 15), ("N", 15), ("O", 15), ("P", 15), ("Q", 15)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "Another section of private bunks and minimal personal storage.",
        "doors": {}
    },

    "Chow Hall": {
        "coords": [("U", 16), ("V", 16), ("W", 16), ("X", 16), ("Y", 16),
                   ("U", 17), ("V", 17), ("W", 17), ("X", 17), ("Y", 17),
                   ("U", 18), ("V", 18), ("W", 18), ("X", 18), ("Y", 18)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "Where the crew gathers for meals. Tables are bolted to the floor.",
        "doors": {}
    },

    "Med Bay": {
        "coords": [("R", 13), ("S", 13), ("T", 13),
                   ("R", 14), ("S", 14), ("T", 14),
                   ("R", 15), ("S", 15), ("T", 15)],
        "locked": True,
        "key": "Bridge Key",
        "items": [],
        "description": "A sterile room with medical beds and diagnostic equipment.",
        "doors": {}
    },

    "Secret Passage 1": {
        "coords": [("H", 5), ("O", 19)],
        "locked": False,
        "items": [],
        "leads_to": "Bridge"
    },

    "Secret Passage 2": {
        "coords": [("M", 21)],
        "locked": False,
        "items": [],
        "leads_to": "Bridge"
    },

    "Secret Passage 3": {
        "coords": [("I", 19)],
        "locked": False,
        "items": [],
        "leads_to": "Engine Room"
    }
}

def get_room(position):
    """Returns a tuple of (room_name, room_data) based on the player's position."""
    for room, data in SHIP_MAP.items():
        if position in data["coords"]:
            return room, data
    return None, None
