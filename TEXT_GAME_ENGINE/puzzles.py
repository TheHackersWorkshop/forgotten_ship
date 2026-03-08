class PuzzleManager:
    def __init__(self, puzzles_data):
        # Store puzzles in memory to track 'solved' status
        if isinstance(puzzles_data, list):
            self.puzzles = {p["id"]: p for p in puzzles_data}
        else:
            self.puzzles = puzzles_data

    def attempt_use(self, item_name, target_name, player, world, ship):
        """
        Standard 'Use Item on Target' logic.
        Example: 'use battery on generator'
        """
        # Find a puzzle that matches this item + target combination
        puzzle = next((p for p in self.puzzles.values()
                       if p.get("item") == item_name
                       and p.get("target") == target_name
                       and not p.get("solved")), None)

        if not puzzle:
            return False, "Nothing happens."

        # Execute the puzzle logic based on its type
        if puzzle["type"] == "unlock_room":
            target_room = puzzle["room"]
            if target_room in world.map:
                world.map[target_room]["locked"] = False
                puzzle["solved"] = True
                return True, puzzle.get("success_msg", f"The {target_room} is now open!")

        elif puzzle["type"] == "reveal_item":
            # Example: Using a 'crowbar' on a 'crate' to reveal a 'key'
            new_item = puzzle["reward_item"]
            new_item["position"] = list(player.position)
            world.items.append(new_item)
            puzzle["solved"] = True
            return True, puzzle.get("success_msg", f"You revealed a {new_item['name']}!")

        return False, "You can't do that yet."

    def check_auto_puzzles(self, player, world):
        """
        Checks for puzzles that solve just by having an item in inventory
        (Classic Zork style: if you have the lamp, the dark room is 'unlocked').
        """
        for p_id, p in self.puzzles.items():
            if p.get("solved"): continue

            if p["type"] == "key_required":
                if player.has_item(p["key"]):
                    target_room = p["room"]
                    if target_room in world.map:
                        world.map[target_room]["locked"] = False
                        p["solved"] = True
                        print(f"[EVENT] You use the {p['key']} to unlock the {target_room}.")
