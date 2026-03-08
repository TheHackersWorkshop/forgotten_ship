class Player:
    def __init__(self, start_pos=("N", 6), health=100, inventory=None):
        # Position is stored as a tuple (e.g., ('A', 5))
        self.position = tuple(start_pos)
        self.health = health
        self.inventory = inventory or []
        self.max_inventory = 4

        # We use sets for fast lookup during gameplay
        self.visited = {self.position}
        self.revealed_coords = set()
        self.visited_dialogue = set()

        # Track triggers/events that have already happened
        self.fired_triggers = set()

    def move(self, direction, ship):
        """
        Moves the player based on a direction string (n, s, e, w).
        Returns (Success, ErrorMessage)
        """
        self.last_position = self.position
        delta = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}
        col, row = self.position

        if direction not in delta:
            return False, "Invalid direction."

        dx, dy = delta[direction]
        # Handle the character-based column (A, B, C...) and integer row
        new_pos = (chr(ord(col) + dx), row + dy)

        if ship.is_walkable(new_pos):
            self.position = new_pos
            self.visited.add(self.position)

            # Auto-reveal room logic for the UI map
            room_name = ship.current_room(self.position)
            if room_name:
                self.revealed_coords.update(ship.room_coords[room_name])
            return True, None

        return False, "You cannot go that way."

    def add_item(self, item):
        """Standard inventory check."""
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
            return True
        return False

    def has_item(self, item_name):
        """Standard feature: Check for puzzle requirements."""
        return any(i['name'].lower() == item_name.lower() for i in self.inventory)

    def get_inventory_state(self):
        """Returns a JSON-serializable version of the player state."""
        return {
            "position": self.position,
            "health": self.health,
            "inventory": self.inventory,
            "visited": [list(p) for p in self.visited], # Convert sets of tuples to lists of lists
            "revealed": [list(p) for p in self.revealed_coords],
            "fired_triggers": list(self.fired_triggers)
        }

    def load_inventory_state(self, data):
        """Restores player state from a dictionary (the save file)."""
        self.position = tuple(data["position"])
        self.health = data["health"]
        self.inventory = data["inventory"]
        self.visited = set(tuple(p) for p in data["visited"])
        self.revealed_coords = set(tuple(p) for p in data["revealed"])
        self.fired_triggers = set(data.get("fired_triggers", []))
