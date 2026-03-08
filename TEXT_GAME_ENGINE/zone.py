class Ship:
    def __init__(self, map_data):
        self.map = map_data
        self.room_coords = {}
        self.doors = {}

        for room_name, room_data in self.map.items():
            coords = set(tuple(pos) for pos in room_data.get("coords", []))
            self.room_coords[room_name] = coords

            for door_name, door in room_data.get("doors", {}).items():
                entry = tuple(door["entry"])
                self.doors[entry] = {"exit": tuple(door["exit"]), "room": room_name}

    def get_room_at(self, pos):
        for name, coords in self.room_coords.items():
            if pos in coords: return name
        return None

    def is_walkable(self, pos):
        if pos in self.doors: return True
        room = self.get_room_at(pos)
        if room:
            return not self.map[room].get("locked", False)
        return False
