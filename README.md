# Text Adventure Game Engine
**Copyright 2026**

A modular, JSON-driven text adventure engine built for terminal environments (optimized for Debian/Linux). This engine separates core game logic from world data, allowing developers to create complex narratives, combat systems, and exploration mechanics without modifying the Python source code.

## Features
* **Multi-World Support:** Automatically scans the `worlds/` directory for unique game simulations.
* **JSON-Driven Data:** Rooms, items, enemies, and dialogue are all defined in standard JSON format.
* **Dynamic Dialogue System:** Supports character-specific inner thoughts and NPC logs with priority and trigger logic.
* **Persistent State:** Integrated save/load system that tracks player health, inventory, and world exploration.
* **ASCII Graphics:** Customizable global and world-specific splash screens.

---

## Technical Architecture
The engine relies on a specific folder structure within the `worlds/` directory to initialize a simulation:

```text
/your_project_root/
├── main.py             # Main game loop and input handler
├── world_loader.py     # Data parsing and state management
├── ui.py               # ASCII rendering and screen management
├── engine_splash.txt   # Global "Hacker's Workshop" logo
└── worlds/
    └── your_world_name/
        ├── map.json        # Room definitions and coordinates
        ├── items.json      # Objects, equipment, and NPCs
        ├── enemies.json    # Monster stats and placement
        ├── dialogue.json   # Narrative triggers and lines
        └── splash.txt      # World-specific ASCII art
