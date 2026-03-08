class Ship:
    def __init__(self, map_data, items_data=None):
        # We store the raw data but also build optimized lookups
        self.map = map_data
        self.items = items_data or []
        self.room_coords = {}
        self.doors = {}

        # 1. Initialize the Spatial Index
        for room_name, room_data in self.map.items():
            # Convert JSON lists [["N", 6]] into Python sets of tuples {("N", 6)}
            coords = set(tuple(pos) for pos in room_data.get("coords", []))
            self.room_coords[room_name] = coords

            # 2. Register Exit/Entry points (Doors)
            for door_name, door in room_data.get("doors", {}).items():
                entry = tuple(door["entry"])
                self.doors[entry] = {
                    "exit": tuple(door["exit"]),
                    "room": room_name,
                    "target_room": door.get("target_room") # Which room this leads to
                }

    def current_room(self, pos):
        """Returns the ID of the room the player is standing in."""
        for room, coords in self.room_coords.items():
            if pos in coords:
                return room
        return None

    def is_walkable(self, pos, world_map_state=None):
        """
        Determines if the player can move to a coordinate.
        Standard Feature: Checks the LIVE world state for locked doors.
        """
        # If it's a door tile, check if the specific room/door is locked
        if pos in self.doors:
            room_id = self.doors[pos]["room"]
            # Use the passed-in state (memory) to see if it's currently locked
            if world_map_state and world_map_state.get(room_id, {}).get("locked", False):
                return False
            return True

        # Check if the tile belongs to a known room
        room = self.current_room(pos)
        if room:
            # If the room itself is marked as locked in the live memory
            if world_map_state and world_map_state.get(room, {}).get("locked", False):
                return False
            return True

        return False # It's a wall or void space

    def get_adjacent_coords(self, pos):
        """Useful for auto-revealing nearby tiles in the UI."""
        c, r = pos
        return [
            (chr(ord(c)), r + 1), # North
            (chr(ord(c)), r - 1), # South
            (chr(ord(c) + 1), r), # East
            (chr(ord(c) - 1), r)  # West
        ]
