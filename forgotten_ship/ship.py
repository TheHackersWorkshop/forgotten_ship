class Ship:
    def __init__(self, map_data, items_data=None):
        self.map = map_data
        self.items = items_data or []

        self.room_coords = {}
        self.doors = {}

        for room_name, room_data in self.map.items():
            coords = set(tuple(pos) for pos in room_data.get("coords", []))
            self.room_coords[room_name] = coords

            for door_name, door in room_data.get("doors", {}).items():
                entry = tuple(door["entry"])
                exit_ = tuple(door["exit"])
                self.doors[entry] = {
                    "exit": exit_,
                    "locked": door.get("locked", False),
                    "room": room_name
                }

            # Add secret passages as doors if they are revealed
            for sp_name, sp in room_data.get("secret_passages", {}).items():
                if sp.get("revealed"):
                    entry = tuple(sp["entry"])
                    exit_ = tuple(sp["exit"])
                    self.doors[entry] = {
                        "exit": exit_,
                        "locked": False,
                        "room": room_name,
                        "secret": True
                    }

    def current_room(self, pos):
        for room, coords in self.room_coords.items():
            if pos in coords:
                return room
        return None

    def is_walkable(self, pos):
        room = self.current_room(pos)
        if room:
            # Prevent entering locked rooms
            room_data = self.map.get(room, {})
            if room_data.get("locked", False):
                return False
            return True
        return pos in self.doors



    def is_door(self, pos):
        return pos in self.doors

    def door_locked(self, pos):
        door = self.doors.get(pos)
        return door["locked"] if door else False

    def door_exit(self, pos):
        door = self.doors.get(pos)
        return door["exit"] if door else None
