# inventory.py


class Item:
    def __init__(self, name, category, description=""):
        self.name = name
        self.category = category  # e.g., "key", "tool", "clue", "aid", "npc"
        self.description = description

    def __repr__(self):
        return f"{self.name} ({self.category})"


# Master list of all in-game items
ITEM_CATALOG = {
    # Keys
    "Bridge Key": Item("Bridge Key", "key", "Opens the Bridge."),
    "Server Key": Item("Server Key", "key", "Grants access to the Server Room."),
    "Weapons Key": Item("Weapons Key", "key", "Unlocks the Weapons Room."),
    "Toolkit": Item("Toolkit", "key", "Needed to unlock and repair the Engine Room."),
    "Airlock Key": Item("Airlock Key", "key", "Used to open the Airlock."),
    "Room 1 Key": Item("Room 1 Key", "key", "Unlocks Sleeping Quarters 1."),
    "Room 2 Key": Item("Room 2 Key", "key", "Unlocks Sleeping Quarters 2."),
    "Room 3 Key": Item("Room 3 Key", "key", "Unlocks Sleeping Quarters 3."),
    "Room 4 Key": Item("Room 4 Key", "key", "Unlocks Sleeping Quarters 4."),

    # Tools
    "Flashlight": Item("Flashlight", "tool", "Illuminates dark areas."),
    "Knife": Item("Knife", "tool", "Can be used in combat."),
    "Repair Tools": Item("Repair Tools", "tool", "Used to fix damaged systems."),
    "Ammo": Item("Ammo", "tool", "Required to operate certain weapons."),
    "Plaster": Item("Plaster", "tool", "Can be used to patch small wounds."),

    # Aids / Consumables
    "Medkit": Item("Medkit", "aid", "Restores a large amount of health."),
    "Painkillers": Item("Painkillers", "aid", "Restores a small amount of health."),
    "Food": Item("Food", "aid", "Restores a bit of stamina."),
    "Alcohol": Item("Alcohol", "aid", "Reduces stress, but affects clarity."),

    # NPC
    "Navigator Rachel": Item("Navigator Rachel", "npc", "The only other surviving crew member."),

    # Escape/Story Progression
    "Escape Pod": Item("Escape Pod", "tool", "The only way off the ship."),
}


def apply_item_effect(player, item):
    """
    Applies the effect of the item to the player or game state.

    :param player: The Player object using the item
    :param item: The Item object being used
    :return: True if the item had an effect and should be consumed, else False
    """
    if item.category == "aid":
        if item.name == "Medkit":
            player.restore_health(50)
            print("You used a Medkit. Health restored by 50.")
            return True

        elif item.name == "Painkillers":
            player.restore_health(20)
            print("You took Painkillers. Health restored by 20.")
            return True

        elif item.name == "Food":
            print("You ate some food. Slightly more energized.")
            return True

        elif item.name == "Alcohol":
            print("You drank Alcohol. Feeling calmer... or is it fuzzier?")
            return True

    elif item.category == "npc":
        if item.name == "Navigator Rachel":
            state = load_game_state()
            if state.get("rachel_moved"):
                print("Rachel has already been moved to the med bay.")
                return False

            current_room = player.get_current_room_name()
            if current_room.lower() in ["sleeping quarters 2", "room 2"]:
                update_game_state("rachel_moved", True)
                print("You helped Rachel to the med bay. She’s now safe.")
                return True
            else:
                print("You need to be in Rachel's room (Sleeping Quarters 2) to move her.")
                return False

    elif item.category == "tool":
        print(f"You used {item.name}, but it had no immediate effect.")
        return True

    print(f"{item.name} can't be used directly.")
    return False
