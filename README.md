# Forgotten Ship - A text-based sci-fi thriller
Text based game in Python

Forgotten Ship is a work-in-progress terminal-based exploration game written in Python. While the story is still in development, the foundational mechanics and systems are already functional — making this an open invitation to explore, test, and leave feedback on the game’s systems, structure, and feel.

The game is currently free, designed as a narrative-driven adventure where players explore an abandoned ship, manage their inventory, uncover secrets, and navigate between interconnected rooms via a coordinate-based map.

What the Game Does
Forgotten Ship builds an interactive world where:

Players navigate using coordinate-based movement on a 2D ship grid.

Line-of-sight and flashlight mechanics govern what the player can see.

Doors may be locked or unlocked based on the player’s inventory (keys).

Each room is mapped with descriptive metadata and compartmentalized items.

Items can be picked up, used, dropped, or stored, and players have weight limits.

Game state is persistent — inventory, player position, room items, and certain flags are saved and restored.

Magic storage containers allow certain rooms or boxes to retain item data across saves.

The player’s position, health, and progress are tracked in a modular and serializable form.

Players can “look” around based on visibility and scan adjacent tiles for items.

This setup is already built to support more complex features such as puzzles, enemies, or branching narrative — but right now the focus is entirely on the interactive structure.

⚙️ Current Status
Incomplete — The narrative, dialogue, and puzzle elements are not yet finalized.

Playable — The game can be run, explored, and interacted with via the terminal.

Expandable — Room data and item catalogs are structured in a way that supports content growth.

You can:

Walk around the ship

Pick up and use items

Move between rooms (using doors when available)

Save/load your progress

Interact with room descriptions and inventory limits

You cannot yet:

Complete a storyline

Encounter characters or enemies

Solve end-game puzzles

 How to Play

Copy
Edit
python main.py
Once inside the game:

Use directional commands like move bow, move stern, move port, move starboard

Use look to scan your surroundings

Use status, inventory, pickup <item>, drop <item>, or use <item> as applicable

Use save and load to persist or restore game progress

 Feedback
This game is actively being worked on, especially the storyline and event system.

If you’ve played around and have comments about:

Mechanics that feel solid or confusing

Suggestions for better room interaction

Inventory balancing or item effects

Bugs or logic gaps

Please feel free to open an issue or leave a comment.

 Structure Highlights
player.py – Core player logic, including movement, inventory, health, vision, and state tracking.

ship.py – Defines the room layout (SHIP_MAP), coordinate data, and helper utilities.

inventory.py – Item definitions (ITEM_CATALOG), item class, and item-based effects.

utils.py – Handles save/load functions, item persistence, and JSON interaction.

 License
Free for anyone to test and explore.
Story and final release will be announced later.
