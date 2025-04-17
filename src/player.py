import json
import os
import sys
from src.inventory import ITEM_CATALOG, Item, apply_item_effect
from src.ship import SHIP_MAP, get_room


class Player:
    def __init__(self, name="Ryan", position=("I", 5), has_flashlight=False):
        self.name = name
        self.position = position
        self.inventory = []
        self.health = 100
        self.max_inventory = 5
        self.has_flashlight = has_flashlight
        self.explored_coords = []  # Added to support map tracking
        self.doors_coords = []     # Added to support map tracking

    def is_alive(self):
        return self.health > 0

    def move(self, direction, steps=1):
        if not self.is_alive():
            print(f"{self.name} cannot move because they are dead.")
            return

        if direction not in ["bow", "stern", "port", "starboard"]:
            print(f"Invalid direction: {direction}")
            return

        x, y = self.position
        moved = 0

        for _ in range(steps):
            if direction == "bow":
                y += 1
            elif direction == "stern":
                y -= 1
            elif direction == "port":
                x = chr(ord(x) - 1)
            elif direction == "starboard":
                x = chr(ord(x) + 1)

            new_position = (x, y)

            current_room_name = None
            new_room_name = None

            for room_name, room_data in SHIP_MAP.items():
                if self.position in room_data.get("coords", []):
                    current_room_name = room_name
                if new_position in room_data.get("coords", []):
                    new_room_name = room_name

            if new_room_name is None:
                print(f"Movement stopped — there's no room at {new_position}.")
                break

            if current_room_name == new_room_name:
                self.position = new_position
                moved += 1
                continue

            door_allowed = False
            for room in (current_room_name, new_room_name):
                if room and "doors" in SHIP_MAP[room]:
                    for door_data in SHIP_MAP[room]["doors"].values():
                        entry = door_data.get("entry")
                        exit_ = door_data.get("exit")
                        if ((self.position == entry and new_position == exit_) or
                            (self.position == exit_ and new_position == entry)):
                            if door_data.get("locked", False):
                                key_needed = door_data.get("key")
                                if not self.has_item(key_needed):
                                    print(f"The door is locked. You need the {key_needed}.")
                                    return
                            door_allowed = True
                            break
                if door_allowed:
                    break

            if door_allowed:
                self.position = new_position
                moved += 1
            else:
                print("You can't go that way. There’s a wall or no accessible door.")
                break

        if moved > 0:
            print(f"[Current Position: {self.position}]")
        self.update_room()

    def get_current_room(self):
        for room_name, room_data in SHIP_MAP.items():
            if self.position in room_data["coords"]:
                return room_data
        return None

    def get_current_room_name(self):
        current_room = self.get_current_room()
        if current_room:
            return current_room.get("name", "Unknown Room")
        return "Unknown Room"

    def update_room(self):
        current_room = self.get_current_room()
        if current_room:
            print(f"\nYou are in: {self.get_current_room_name()}")
            print(f"Description: {current_room.get('description', 'No description available.')}")
            print(f"Current Coordinates: {self.position}")
            items = current_room.get("compartment", [])
            item_names = ", ".join([item.name for item in items]) if items else "None"
            print(f"Items found: {item_names}")

    def look(self):
        if not self.is_alive():
            print(f"{self.name} cannot look around because they are dead.")
            return

        print("You look around the room.")
        visible_tiles = self.get_visible_tiles()
        item_list = []

        for coord in visible_tiles:
            for room_data in SHIP_MAP.values():
                if coord in room_data.get("coords", []):
                    for item in room_data.get("compartment", []):
                        item_list.append(f"{item.name} at {coord}")

        print(f"\nYou are in: {self.get_current_room_name()}")
        print(f"Space {self.position}")
        print("Items in visible range:")
        if item_list:
            for entry in item_list:
                print(f"- {entry}")
        else:
            print("You don't see any items nearby.")

    def status(self):
        print(f"\nStatus Report for {self.name}")
        print(f"- Health: {self.health}")
        print(f"- Current Position: {self.position}")
        print(f"- Current Room: {self.get_current_room_name()}")
        print(f"- Carrying {self.get_carry_count()} of {self.max_inventory} non-key items")
        keys = [item.name for item in self.inventory if item.category == "key"]
        print(f"- Keys: {', '.join(keys) if keys else 'None'}")

    def add_item(self, item_name):
        if not self.is_alive():
            print(f"{self.name} cannot pick up items because they are dead.")
            return False

        if item_name not in ITEM_CATALOG:
            print(f"Item '{item_name}' not found in catalog.")
            return False

        item = ITEM_CATALOG[item_name]

        if any(i.name == item.name for i in self.inventory):
            print(f"You already have {item.name} in your inventory.")
            return False

        if item.category == "key":
            self.inventory.append(item)
            print(f"Key added: {item.name}")
            return True

        carry_weight = 2 if item.name.lower() == "rachel" else 1
        if self.get_carry_count() + carry_weight > self.max_inventory:
            print(f"Inventory full. You cannot carry {item.name} right now.")
            return False

        self.inventory.append(item)
        print(f"Item added: {item.name} — {item.description}")
        return True

    def get_carry_count(self):
        count = 0
        for item in self.inventory:
            if item.category != "key":
                if item.name.lower() == "rachel":
                    count += 2
                else:
                    count += 1
        return count

    def drop_item(self, item_name):
        if not self.is_alive():
            print(f"{self.name} cannot drop items because they are dead.")
            return None

        for i, item in enumerate(self.inventory):
            if item.name == item_name:
                removed = self.inventory.pop(i)
                print(f"Dropped: {removed.name}")
                current_room = self.get_current_room()
                if "compartment" not in current_room:
                    current_room["compartment"] = []
                current_room["compartment"].append(item)
                return removed
        print(f"{item_name} not in inventory.")
        return None

    def has_item(self, item_name):
        return any(item.name == item_name for item in self.inventory)

    def restore_health(self, amount):
        if not self.is_alive():
            print(f"{self.name} cannot be healed because they are dead.")
            return
        self.health += amount
        if self.health > 100:
            self.health = 100
        print(f"{self.name}'s health is now {self.health}.")

    def list_inventory(self):
        if not self.inventory:
            print("Your inventory is empty.")
            return
        print("Your inventory contains:")
        for item in self.inventory:
            print(f"- {item.name} ({item.category})")

    def use_door(self):
        current_room = self.get_current_room()
        if not current_room or "doors" not in current_room:
            print("There is no door here.")
            return

        for door_label, door_data in current_room["doors"].items():
            if self.position == door_data.get("entry"):
                if door_data.get("locked"):
                    key_needed = door_data.get("key")
                    if not self.has_item(key_needed):
                        print(f"The {door_label} is locked. You need the {key_needed}.")
                        return
                self.position = door_data["exit"]
                print(f"You go through the {door_label}.")
                return

        print("There is no usable door at your location.")

    def save(self, filename="savegame.json"):
        data = {
            "name": self.name,
            "position": self.position,
            "inventory": [item.name for item in self.inventory],
            "health": self.health,
            "max_inventory": self.max_inventory,
            "has_flashlight": self.has_flashlight,
            "explored_coords": self.explored_coords,
            "doors_coords": self.doors_coords,
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Game saved to {filename}.")

    @classmethod
    def load(cls, filename="savegame.json"):
        if not os.path.exists(filename):
            print(f"Save file {filename} not found. Starting a new game.")
            return cls()

        with open(filename, "r") as f:
            data = json.load(f)

        player = cls(name=data.get("name", "Ryan"),
                     position=tuple(data.get("position", ("I", 5))),
                     has_flashlight=data.get("has_flashlight", False))

        player.health = data.get("health", 100)
        player.max_inventory = data.get("max_inventory", 5)
        player.explored_coords = [tuple(coord) for coord in data.get("explored_coords", [])]
        player.doors_coords = [tuple(coord) for coord in data.get("doors_coords", [])]

        inventory_names = data.get("inventory", [])
        for item_name in inventory_names:
            if item_name in ITEM_CATALOG:
                player.inventory.append(ITEM_CATALOG[item_name])
            else:
                print(f"Warning: {item_name} not found in ITEM_CATALOG. Skipped.")

        print(f"Game loaded from {filename}.")
        return player

    def game_over(self):
        print("\nGAME OVER")
        print("Thank you for playing Forgotten Ship.\n")
        choice = input("Would you like to start over? (yes/no): ").strip().lower()
        if choice == "yes":
            from main import main
            main()
        else:
            sys.exit(0)

    def take_damage(self, amount):
        if not self.is_alive():
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print(f"{self.name} has died.")
            self.game_over()
        else:
            print(f"{self.name} took {amount} damage, health is now {self.health}.")

    # --- Vision and Map Awareness ---
    def get_visible_tiles(self):
        visible = set()
        x, y = self.position
        room_name, room_data = get_room(self.position)
        if not room_data:
            return visible
        room_coords = set(room_data["coords"])
        visible.add((x, y))

        if self.has_flashlight:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx = chr(ord(x) + dx)
                    ny = y + dy
                    if (nx, ny) in room_coords:
                        visible.add((nx, ny))
        else:
            for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
                nx = chr(ord(x) + dx)
                ny = y + dy
                if (nx, ny) in room_coords:
                    visible.add((nx, ny))

        return visible

    def can_see(self, coord):
        return coord in self.get_visible_tiles()

    def show_map(self):
        current_room = self.get_current_room()
        if not current_room:
            print("Cannot display map - you're not in a valid room.")
            return

        ship_width = 10
        ship_height = 10
        ship_map = [["." for _ in range(ship_width)] for _ in range(ship_height)]
        x, y = self.position
        x_idx = ord(x) - ord("A")
        y_idx = y - 1

        if 0 <= x_idx < ship_width and 0 <= y_idx < ship_height:
            ship_map[y_idx][x_idx] = "P"

        print("Ship Map:")
        for row in ship_map:
            print(" ".join(row))
        print(f"\nYou are currently in room at position {self.position}.")
