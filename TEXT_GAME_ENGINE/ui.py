import os

def display_splash(world_path=None):
    """Prints ASCII art. If world_path is provided, looks for a specific splash."""
    clear_screen()
    splash_file = "engine_splash.txt" # Default engine logo

    if world_path:
        specific_splash = os.path.join(world_path, "splash.txt")
        if os.path.exists(specific_splash):
            splash_file = specific_splash

    if os.path.exists(splash_file):
        with open(splash_file, 'r') as f:
            print(f.read())
            input("\n[ Press Enter to Begin ]")
    else:
        # Fallback if no file exists
        print("\n=== WELCOME TO THE FORGOTTEN SHIP ===")
        input("\n[ Press Enter to Begin ]")

def clear_screen():
    """Clears the terminal for a cleaner 'game' feel."""
    # Works for both Windows (nt) and Linux/macOS (posix)
    os.system('cls' if os.name == 'nt' else 'clear')

def render_map(ship, player, items, enemies):
    """
    Renders a coordinate-based ASCII map with a Fog of War radius.
    Only shows items and monsters within a certain distance.
    """
    width, height = 26, 25
    # Initialize an empty grid
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Fog of War settings
    view_distance = 4
    px, py = player.position
    # Convert 'A'-'Z' to index 0-25 safely
    px_idx = ord(px.upper()) - 65

    # 1. DRAW PERMANENT MEMORY (Discovered Tiles)
    # player.revealed_coords should be a set of (char, int) tuples
    for (c, r) in player.revealed_coords:
        col_idx = ord(c.upper()) - 65
        # Grid index is row-1, col_idx
        if 0 <= col_idx < width and 0 <= r-1 < height:
            grid[r-1][col_idx] = "."

    # 2. DRAW DYNAMIC OBJECTS (Items & Enemies)
    # We only draw these if they are within the Manhattan distance 'view_distance'

    # Draw Items
    for i in items:
        if "position" in i:
            ix, iy = i["position"][0], i["position"][1]
            ix_idx = ord(ix.upper()) - 65
            # Manhattan Distance Calculation
            dist = abs(ix_idx - px_idx) + abs(iy - py)
            if dist <= view_distance:
                grid[iy-1][ix_idx] = "I"

    # Draw Enemies
    for e in enemies:
        if e.alive:
            ex, ey = e.pos[0], e.pos[1]
            ex_idx = ord(ex.upper()) - 65
            dist = abs(ex_idx - px_idx) + abs(ey - py)
            if dist <= view_distance:
                grid[ey-1][ex_idx] = "M"

    # 3. DRAW PLAYER (Always visible)
    grid[py-1][px_idx] = "P"

    # --- UI COMPOSITION ---
    current_room = ship.current_room(player.position)
    room_display = current_room.replace("_", " ").upper() if current_room else "DEEP SPACE"

    # Header
    print("\n" + "="*45)
    print(f" LOCATION: {room_display:<18} | HP: {player.health}")
    print("="*45)

    # Grid Rendering (Top-down)
    # We iterate from height-1 down to 0 so Row 25 is at the top of the screen
    for y in range(height - 1, -1, -1):
        row_str = "".join(grid[y])
        # Only print rows that actually have something discovered to save vertical space
        if row_str.strip():
            print(f"{y+1:2} | {row_str}")

    # Footer/Legend
    print("="*45)
    print(" P: You  .: Floor  I: Item  M: Monster  +: Door")
    print("="*45)

def display_message(msg):
    """Prints game events with a visual prompt."""
    if msg:
        print(f"\n >> {msg}")

def combat_ui(enemy, player):
    """A specialized display for when combat is active."""
    print("\n" + "!"*45)
    print(f" FIGHT: {enemy.name.upper()} ")
    print(f" ENEMY HP: {enemy.health} | YOUR HP: {player.health}")
    print("!"*45)
