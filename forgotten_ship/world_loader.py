import json
import os
import random

class World:
    def __init__(self, world_name, new_game=True):
        self.base_path = os.path.join("worlds", world_name)

        # Load files
        self.map = self._load("map.json")
        self.items = self._load("items.json")
        self.enemies = self._load("enemies.json")
        self.logs = self._load("logs.json")
        self.puzzles = self._load("puzzles.json")

        self.stage = 0

        # track used positions to avoid overlapping placements
        self._used_positions = set()

        if new_game:
            # Mark positions that already exist on items (and player's start pos)
            for item in self.items:
                if "position" in item and item["position"]:
                    self._used_positions.add(tuple(item["position"]))
                if item.get("type") == "player" and "start_pos" in item:
                    self._used_positions.add(tuple(item["start_pos"]))

            # Randomly place non-constant items
            for item in self.items:
                if not item.get("constant", False) and "position" not in item:
                    pos = self._place_random()
                    item["position"] = pos
                    self._used_positions.add(tuple(pos))

            # Place enemies on random free tiles
            for enemy in self.enemies:
                if not enemy.get("location"):
                    pos = self._place_random()
                    enemy["location"] = pos
                # mark alive state
                enemy["alive"] = True

    def _load(self, filename):
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            print(f"Warning: {filename} not found in {self.base_path}")
            return []
        with open(path, "r") as f:
            return json.load(f)

    def _place_random(self):
        # Choose a random coordinate from room coords excluding already used positions
        all_coords = []
        for room_data in self.map.values():
            all_coords.extend(room_data.get("coords", []))

        choices = [c for c in all_coords if tuple(c) not in self._used_positions]
        if not choices:
            # fallback to any coord
            return list(random.choice(all_coords)) if all_coords else ["N", 6]
        choice = random.choice(choices)
        return list(choice)
