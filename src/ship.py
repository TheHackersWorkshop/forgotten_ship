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
                "exit": ("H", 5),
                "revealed": False
            }
        }
    },

    "Server Room": {
        "coords": [("M", 19), ("N", 19), ("O", 19),
                   ("M", 20), ("N", 20), ("O", 20),
                   ("M", 21), ("N", 21), ("O", 21)],
        "locked": True,
        "key": "Server Key",
        "doors": {
            "to corridor": {
                "entry": ("N", 21),
                "exit": ("N", 22),
                "locked": False
            }
        }
    },

    "Weapons Room": {
        "coords": [("P", 19), ("Q", 19),
                   ("P", 20), ("Q", 20)],
        "locked": True,
        "key": "Weapons Key",
        "doors": {
            "to corridor": {
                "entry": ("Q", 20),
                "exit": ("Q", 21),
                "locked": False
            }
        }
    },

    "Engine Room": {
        "coords": [("C", 5), ("D", 5), ("E", 5), ("F", 5), ("G", 5), ("H", 5),
                   ("C", 6), ("D", 6), ("E", 6), ("F", 6), ("G", 6), ("H", 6),
                   ("C", 7), ("D", 7), ("E", 7), ("F", 7), ("G", 7), ("H", 7)],
        "locked": True,
        "key": "Engine Key",
        "doors": {
            "to Cargo Bay": {
                "entry": ("H", 6),
                "exit": ("I", 6),
                "locked": False
            }
        },
        "secret_passages": {
            "to bridge": {
                "entry": ("I", 5),
                "exit": ("H", 19),
                "revealed": False
            }
        }
    },

    "Airlock": {
        "coords": [("I", 3), ("J", 3),
                   ("I", 4), ("J", 4)],
        "locked": False,
        "key": None,
        "doors": {
            "to Cargo Bay": {
                "entry": ("J", 4),
                "exit": ("J", 5),
                "locked": False
            }
        }
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
        "locked": True,
        "key": [],
        "doors": {
            "to Cargo Bay": {"entry": ("J", 10), "exit": ("J", 9), "locked": False},
            "to Sleeping Quarters 1": {"entry": ("I", 11), "exit": ("H", 11), "locked": False},
            "to Sleeping Quarters 2": {"entry": ("L", 11), "exit": ("M", 11), "locked": False},
            "to Sleeping Quarters 3": {"entry": ("I", 14), "exit": ("H", 14), "locked": False},
            "to Sleeping Quarters 4": {"entry": ("L", 14), "exit": ("M", 14), "locked": False},
            "to Chow Hall": {"entry": ("T", 17), "exit": ("U", 17), "locked": False},
            "to Med Bay": {"entry": ("S", 16), "exit": ("S", 17), "locked": False},
            "to Weapons Room": {"entry": ("Q", 21), "exit": ("Q", 20), "locked": False},
            "to Server Room": {"entry": ("N", 22), "exit": ("N", 21), "locked": False},
            "to Bridge": {"entry": ("K", 23), "exit": ("K", 22), "locked": False}
        }
    },

    "Cargo Bay": {
        "coords": [("I", 5), ("J", 5), ("K", 5), ("L", 5), ("M", 5), ("N", 5),
                   ("I", 6), ("J", 6), ("K", 6), ("L", 6), ("M", 6), ("N", 6)],
        "locked": False,
        "key": None,
        "doors": {
            "to Airlock": {"entry": ("J", 5), "exit": ("J", 4), "locked": False},
            "to Corridor": {"entry": ("J", 9), "exit": ("J", 10), "locked": False}
        }
    },

    "Sleeping Quarters 1": {
        "coords": [("C", 10), ("D", 10), ("E", 10), ("F", 10), ("G", 10), ("H", 10),
                   ("C", 11), ("D", 11), ("E", 11), ("F", 11), ("G", 11), ("H", 11)],
        "locked": True,
        "key": "Room 1",
        "doors": {
            "to Corridor": {
                "entry": ("H", 11),
                "exit": ("I", 11),
                "locked": False
            }
        }
    },

    "Sleeping Quarters 2": {
        "coords": [("M", 10), ("N", 10), ("O", 10),
                   ("M", 11), ("N", 11), ("O", 11)],
        "locked": True,
        "key": "Room 2",
        "doors": {
            "to Corridor": {
                "entry": ("M", 11),
                "exit": ("L", 11),
                "locked": False
            }
        }
    },

    "Sleeping Quarters 3": {
        "coords": [("C", 13), ("D", 13), ("E", 13),
                   ("C", 14), ("D", 14), ("E", 14)],
        "locked": True,
        "key": "Room 3",
        "doors": {
            "to Corridor": {
                "entry": ("H", 14),
                "exit": ("I", 14),
                "locked": False
            }
        }
    },

    "Sleeping Quarters 4": {
        "coords": [("M", 13), ("N", 13), ("O", 13),
                   ("M", 14), ("N", 14), ("O", 14)],
        "locked": True,
        "key": "Room 4",
        "doors": {
            "to Corridor": {
                "entry": ("M", 14),
                "exit": ("L", 14),
                "locked": False
            }
        }
    },

    "Chow Hall": {
        "coords": [("U", 16), ("V", 16),
                   ("U", 17), ("V", 17)],
        "locked": False,
        "key": None,
        "doors": {
            "to Corridor": {
                "entry": ("U", 17),
                "exit": ("T", 17),
                "locked": False
            }
        }
    },

    "Med Bay": {
        "coords": [("R", 13), ("S", 13), ("T", 13),
                   ("R", 14), ("S", 14), ("T", 14)],
        "locked": False,
        "key": None,
        "doors": {
            "to Corridor": {
                "entry": ("S", 17),
                "exit": ("S", 16),
                "locked": False
            }
        }
    },

    "Secret Passage 1": {
        "coords": [("H", 5), ("O", 19)],
        "locked": False,
        "leads_to": "Bridge"
    },

    "Secret Passage 2": {
        "coords": [("M", 21)],
        "locked": False,
        "leads_to": "Bridge"
    },

    "Secret Passage 3": {
        "coords": [("I", 19)],
        "locked": False,
        "leads_to": "Engine Room"
    }
}

def get_room(position):
    """Returns a tuple of (room_name, room_data) based on the player's position."""
    for room, data in SHIP_MAP.items():
        if position in data["coords"]:
            return room, data
    return None, None
