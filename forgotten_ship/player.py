import json
import os

class Player:
    def __init__(self, start_pos=("N", 6), world_name="forgotten_ship"):
        self.position = tuple(start_pos)
        self.health = 100
        self.flashlight = False
        self.visited = {self.position}
        self.inventory = []

        # Maximum distinct items player can carry
        self.max_inventory = 4

        self.used_triggers = set()
        self.dialogue = self._load_dialogue(world_name)

    def _load_dialogue(self, world_name):
        path = os.path.join("worlds", world_name, "dialogue.json")
        if not os.path.exists(path):
            print(f"Warning: dialogue.json not found at {path}")
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def move(self, direction, ship):
        delta = {"n": (0, 1), "s": (0, -1), "e": (1, 0), "w": (-1, 0)}
        if direction not in delta:
            return None, "Invalid direction."

        col, row = self.position
        dx, dy = delta[direction]
        new_pos = (chr(ord(col) + dx), row + dy)

        if not ship.is_walkable(new_pos):
            return None, "You hit a wall."
        if ship.is_door(new_pos) and ship.door_locked(new_pos):
            return None, "The door is locked."

        self.position = new_pos
        self.visited.add(new_pos)

        dialogue = self.trigger_dialogue(ship.current_room(new_pos))
        return dialogue, None

    def trigger_dialogue(self, room, character="ryan"):
        char_data = self.dialogue.get(character)
        if not char_data or not room:
            return None

        # Normalize room name to match dialogue keys (e.g., 'Cargo Bay' -> 'cargo_bay')
        room_key = room.lower().replace(" ", "_")
        room_lines = char_data.get(room_key) or []
        room_lines = sorted(room_lines, key=lambda d: d["priority"])

        for entry in room_lines:
            trigger = entry.get("trigger")
            if trigger is None:
                continue
            repeatable = entry.get("repeatable", False)
            if not repeatable and trigger in self.used_triggers:
                continue
            self.used_triggers.add(trigger)
            return entry
        return None

    def visible_tiles(self, ship):
        radius = 5 if self.flashlight else 3
        visible = set()
        px, py = self.position
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                tile = (chr(ord(px) + dx), py + dy)
                if ship.is_walkable(tile):
                    visible.add(tile)
        return visible

    def add_item(self, item):
        """Add an item with stacking and inventory limit checks.

        Returns True on success, False if inventory full.
        """
        # If stackable, merge into existing slot
        if item.get("type") == "consumable" and item.get("stackable"):
            for inv in self.inventory:
                if inv.get("id") == item.get("id"):
                    inv["quantity"] = inv.get("quantity", 1) + item.get("quantity", 1)
                    return True

        # New distinct item -> check slot limit
        if len(self.inventory) >= self.max_inventory:
            return False

        # Ensure consumables carry a quantity
        if item.get("type") == "consumable":
            item["quantity"] = item.get("quantity", 1)

        self.inventory.append(item)
        return True

    def has_item(self, item_id):
        for item in self.inventory:
            if item.get("id") == item_id:
                return True
        return False

    def use_item(self, item, world=None, ship=None, pm=None):
        """Use an item from inventory. Returns True if used, False otherwise."""
        if item.get("id") == "flashlight" or item.get("name", "").lower() == "flashlight":
            self.flashlight = not self.flashlight
            return True

        if item.get("type") == "consumable":
            heal = item.get("heal", 0)
            item["quantity"] = item.get("quantity", 1) - 1
            self.health = min(100, self.health + heal)
            if item["quantity"] <= 0:
                self.inventory.remove(item)
            return True

        if item.get("type") == "key":
            opens = item.get("opens")
            if opens and world and world.map.get(opens, {}).get("locked", False):
                world.map[opens]["locked"] = False
                # remove key from inventory after use
                try:
                    self.inventory.remove(item)
                except ValueError:
                    pass
                return True
            return False

        return False

    def drop_item(self, item_id, world):
        """Drop an item into a storage at the player's current position.
        Returns True on success, False if no storage here or item missing."""
        # Find storage at player position
        storage = None
        for s in world.items:
            if s.get("type") == "storage" and tuple(s.get("position")) == self.position:
                storage = s
                break
        if not storage:
            return False

        for it in list(self.inventory):
            if it.get("id") == item_id:
                # put into storage contents
                storage.setdefault("contents", []).append({"id": it["id"], "name": it.get("name"), "quantity": it.get("quantity", 1)})
                try:
                    self.inventory.remove(it)
                except ValueError:
                    pass
                return True
        return False

    def take_from_storage(self, item_id, world):
        # Find storage at player position
        storage = None
        for s in world.items:
            if s.get("type") == "storage" and tuple(s.get("position")) == self.position:
                storage = s
                break
        if not storage:
            return False

        contents = storage.setdefault("contents", [])
        for entry in list(contents):
            if entry.get("id") == item_id:
                # respect inventory limit
                if len(self.inventory) >= self.max_inventory and not any(inv.get("id") == item_id and inv.get("type") == "consumable" for inv in self.inventory):
                    return False
                # find original item in world to restore reference (if exists)
                original = next((i for i in world.items if i.get("id") == item_id), None)
                if original:
                    # restore quantity if consumable
                    if original.get("type") == "consumable":
                        q = entry.get("quantity", 1)
                        original["quantity"] = q
                        self.add_item(original)
                    else:
                        self.add_item(original)
                else:
                    # fallback: create basic item
                    self.add_item({"id": entry["id"], "name": entry.get("name"), "type": "misc"})
                contents.remove(entry)
                return True
        return False
