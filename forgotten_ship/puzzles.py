import json
import os

class PuzzleManager:
    def __init__(self, world_name):
        self.world_name = world_name
        self.puzzles = self.load_puzzles()

    def load_puzzles(self):
        path = os.path.join("worlds", self.world_name, "puzzles.json")
        if not os.path.exists(path):
            print(f"Warning: puzzles.json not found at {path}")
            return {}
        with open(path, "r") as f:
            data = json.load(f)
        # Convert list to dict keyed by id
        if isinstance(data, list):
            return {p["id"]: p for p in data}
        return data

    def get_puzzle(self, puzzle_id):
        return self.puzzles.get(puzzle_id)

    def attempt_puzzle(self, puzzle_id, player=None, world=None):
        puzzle = self.get_puzzle(puzzle_id)
        if not puzzle:
            print("No puzzle found.")
            return False

        if puzzle.get("solved"):
            print("Puzzle already solved.")
            return False

        ptype = puzzle.get("type")

        if ptype == "switch_sequence":
            print(puzzle.get("description", "Solve the puzzle:"))
            answer = input("> ").strip()
            if answer.lower() == puzzle.get("solution", "").lower():
                print(puzzle.get("success_text", "Correct!"))
                puzzle["solved"] = True
                reward = puzzle.get("reward")
                if reward and world:
                    for item in world.items:
                        if item.get("id") == reward:
                            coords = world.map.get(puzzle.get("room"), {}).get("coords", [])
                            if coords:
                                item["position"] = list(coords[0])
                                print(f"{item['name']} has been revealed in {puzzle.get('room')}.")
                                if hasattr(world, "_used_positions"):
                                    world._used_positions.add(tuple(item["position"]))
                # support revealing secret passages via puzzle config
                reveal = puzzle.get("reveal")
                if reveal and world:
                    rroom = reveal.get("room")
                    rpass = reveal.get("passage")
                    if rroom in world.map and rpass in world.map[rroom].get("secret_passages", {}):
                        world.map[rroom]["secret_passages"][rpass]["revealed"] = True
                        print(f"A secret passage '{rpass}' in {rroom} has been revealed.")
                return True
            else:
                print(puzzle.get("failure_text", "Wrong answer."))
                return False

        elif ptype == "multi_step":
            steps = puzzle.get("steps", [])
            max_attempts = puzzle.get("attempts", 3)
            print(puzzle.get("description", "Perform the sequence of steps."))
            for attempt in range(max_attempts):
                ok = True
                for idx, step in enumerate(steps):
                    ans = input(f"Step {idx+1}: ").strip()
                    if ans.lower() != step.lower():
                        print(puzzle.get("step_failure_text", "Incorrect step."))
                        ok = False
                        break
                if ok:
                    print(puzzle.get("success_text", "Correct!"))
                    puzzle["solved"] = True
                    reward = puzzle.get("reward")
                    if reward and world:
                        for item in world.items:
                            if item.get("id") == reward:
                                coords = world.map.get(puzzle.get("room"), {}).get("coords", [])
                                if coords:
                                    item["position"] = list(coords[0])
                                    print(f"{item['name']} has been revealed in {puzzle.get('room')}.")
                                    if hasattr(world, "_used_positions"):
                                        world._used_positions.add(tuple(item["position"]))
                    reveal = puzzle.get("reveal")
                    if reveal and world:
                        rroom = reveal.get("room")
                        rpass = reveal.get("passage")
                        if rroom in world.map and rpass in world.map[rroom].get("secret_passages", {}):
                            world.map[rroom]["secret_passages"][rpass]["revealed"] = True
                            print(f"A secret passage '{rpass}' in {rroom} has been revealed.")
                    return True
                else:
                    print(f"Attempt {attempt+1} failed.")
            print(puzzle.get("failure_text", "Failed to complete sequence."))
            return False

        elif ptype == "timed_sequence":
            import time
            steps = puzzle.get("steps", [])
            time_limit = puzzle.get("time_limit", 10)
            print(puzzle.get("description", f"Complete the sequence within {time_limit} seconds."))
            start = time.time()
            for idx, step in enumerate(steps):
                ans = input(f"Step {idx+1}: ").strip()
                if time.time() - start > time_limit:
                    print(puzzle.get("failure_text", "Time's up."))
                    return False
                if ans.lower() != step.lower():
                    print(puzzle.get("step_failure_text", "Incorrect step."))
                    return False
            if time.time() - start <= time_limit:
                print(puzzle.get("success_text", "Correct!"))
                puzzle["solved"] = True
                reward = puzzle.get("reward")
                if reward and world:
                    for item in world.items:
                        if item.get("id") == reward:
                            coords = world.map.get(puzzle.get("room"), {}).get("coords", [])
                            if coords:
                                item["position"] = list(coords[0])
                                print(f"{item['name']} has been revealed in {puzzle.get('room')}.")
                                if hasattr(world, "_used_positions"):
                                    world._used_positions.add(tuple(item["position"]))
                reveal = puzzle.get("reveal")
                if reveal and world:
                    rroom = reveal.get("room")
                    rpass = reveal.get("passage")
                    if rroom in world.map and rpass in world.map[rroom].get("secret_passages", {}):
                        world.map[rroom]["secret_passages"][rpass]["revealed"] = True
                        print(f"A secret passage '{rpass}' in {rroom} has been revealed.")
                return True
            return False

        elif ptype == "key_required":
            key_id = puzzle.get("key")
            if not player or not player.has_item(key_id):
                print("You don't have the required key.")
                return False
            # optionally confirm key consumption
            consume = puzzle.get("consume_key", True)
            if consume:
                confirm = input(f"Use {key_id} to unlock {puzzle.get('room')}? (y/n) ").lower().strip()
                if confirm != 'y':
                    print("Unlock cancelled.")
                    return False
            # remove key from player's inventory if present
            for it in list(player.inventory):
                if it.get("id") == key_id:
                    try:
                        player.inventory.remove(it)
                    except ValueError:
                        pass
                    break
            room = puzzle.get("room")
            if world and room in world.map:
                world.map[room]["locked"] = False
                puzzle["solved"] = True
                print(f"{room} has been unlocked.")
                return True
            return False

        else:
            print("Unknown puzzle type.")
            return False
