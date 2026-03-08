import json
import os
import random
from enemy import Enemy

class World:
    def __init__(self, world_name, save_file=None):
        self.world_name = world_name
        # Points to the specific subfolder in /worlds/
        self.base_path = os.path.join("worlds", world_name)
        self.save_path = save_file or f"{world_name}_save.json"

        # Placeholders for game data
        self.map = {}
        self.items = []
        self.enemies = []
        self.dialogue = {}
        self.active_enemies = []
        self._used_positions = set()

    @staticmethod
    def list_available_worlds():
        """Scans the 'worlds' directory for folders containing a map.json."""
        if not os.path.exists("worlds"):
            try:
                os.makedirs("worlds")
            except OSError:
                pass
            return []

        # Returns names of folders that contain a map.json file
        return [d for d in os.listdir("worlds")
                if os.path.isdir(os.path.join("worlds", d))
                and os.path.exists(os.path.join("worlds", d, "map.json"))]

    def _load(self, filename):
        """Internal helper to load JSON files from the specific world folder."""
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            # Return empty dict for map/dialogue, empty list for items/enemies
            return {} if "map" in filename or "dialogue" in filename else []

        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"(!) Warning: {filename} is corrupted.")
                return {} if "map" in filename or "dialogue" in filename else []

    def load_initial_data(self):
        """Performs a fresh load of all world data (New Game)."""
        self.map = self._load("map.json")
        self.items = self._load("items.json")
        self.enemies = self._load("enemies.json")
        self.dialogue = self._load("dialogue.json")

        self._used_positions = set()
        self.place_initial_items()
        self.place_enemies()
        return None  # Indicates no player save data was loaded

    def place_initial_items(self):
        """Registers fixed items and randomizes the rest onto floor tiles."""
        # 1. Register fixed positions (Player start and 'constant' items)
        for item in self.items:
            if "position" in item:
                self._used_positions.add(tuple(item["position"]))
            if item.get("type") == "player" and "start_pos" in item:
                self._used_positions.add(tuple(item["start_pos"]))

        # 2. Gather all available floor coordinates from the map
        all_coords = []
        for room_data in self.map.values():
            all_coords.extend([tuple(c) for c in room_data.get("coords", [])])

        # 3. Randomize items that don't have a fixed 'position'
        for item in self.items:
            if "position" not in item and item.get("type") != "player":
                choices = [c for c in all_coords if c not in self._used_positions]
                if choices:
                    pos = random.choice(choices)
                    item["position"] = list(pos)
                    self._used_positions.add(pos)

    def place_enemies(self):
        """Spawns monsters on available floor tiles not occupied by items."""
        floor_tiles = []
        for room in self.map.values():
            floor_tiles.extend([tuple(c) for c in room.get("coords", [])])

        # Filter out tiles already taken by items/player
        available = [t for t in floor_tiles if t not in self._used_positions]
        random.shuffle(available)

        self.active_enemies = []
        for e_data in self.enemies:
            if available:
                # If the enemy has a fixed location in JSON, use it, else randomize
                if "location" in e_data:
                    spawn_pos = tuple(e_data["location"])
                else:
                    spawn_pos = available.pop()

                e_data["location"] = spawn_pos
                self.active_enemies.append(Enemy(e_data))

    def save_game_state(self, player_obj):
        """Saves current progress, including the state of every enemy and item."""
        state = {
            "map": self.map,
            "items": self.items,
            # We save the dictionary representation of Enemy objects
            "enemies": [e.__dict__ for e in self.active_enemies],
            "player": {
                "position": player_obj.position,
                "health": player_obj.health,
                "inventory": player_obj.inventory,
                "visited": list(player_obj.visited),
                "revealed": list(player_obj.revealed_coords),
                "dialogue_history": list(getattr(player_obj, 'visited_dialogue', []))
            }
        }
        with open(self.save_path, "w") as f:
            json.dump(state, f, indent=4)
        print(f"\n[ System: Game state written to {self.save_path} ]")

    def load_game_state(self):
        """Loads a saved state and reconstructs the world objects."""
        if not os.path.exists(self.save_path):
            return None

        with open(self.save_path, "r") as f:
            state = json.load(f)
            self.map = state["map"]
            self.items = state["items"]
            # Re-map dialogue which isn't usually saved but needed for lookups
            self.dialogue = self._load("dialogue.json")
            # Re-initialize Enemy objects from the saved dictionary
            self.active_enemies = [Enemy(e) for e in state["enemies"]]
            return state["player"]
