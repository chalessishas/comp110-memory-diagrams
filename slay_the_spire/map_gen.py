"""Map generation for Slay the Spire - branching path system."""
import random


def generate_map(act=1):
    """Generate a branching map for an act.
    Returns a list of rows (floor 1 to 15), each row containing nodes.
    Each node: {"row": int, "col": int, "type": str, "connections": list of (row, col)}
    """
    rows = 15
    cols = 7
    game_map = [[] for _ in range(rows)]

    # Floor 1: 2-4 starting nodes
    num_starts = random.randint(2, 4)
    start_cols = sorted(random.sample(range(cols), num_starts))
    for c in start_cols:
        game_map[0].append({
            "row": 0, "col": c, "type": "monster",
            "connections": [], "visited": False
        })

    # Generate middle floors (2-14)
    for row in range(1, rows - 1):
        # Each node from previous row connects to 1-2 nodes in next row
        prev_cols = set()
        for node in game_map[row - 1]:
            num_connections = random.randint(1, 2)
            for _ in range(num_connections):
                offset = random.choice([-1, 0, 0, 1])  # bias toward same column
                new_col = max(0, min(cols - 1, node["col"] + offset))
                prev_cols.add(new_col)
                node["connections"].append((row, new_col))

        # Ensure at least 2 nodes per row
        while len(prev_cols) < 2:
            prev_cols.add(random.randint(0, cols - 1))

        for c in sorted(prev_cols):
            node_type = _get_node_type(row, act)
            game_map[row].append({
                "row": row, "col": c, "type": node_type,
                "connections": [], "visited": False
            })

    # Floor 15: Boss
    boss_col = cols // 2
    game_map[rows - 1].append({
        "row": rows - 1, "col": boss_col, "type": "boss",
        "connections": [], "visited": False
    })
    # Connect all floor 14 nodes to boss
    for node in game_map[rows - 2]:
        node["connections"].append((rows - 1, boss_col))

    # Ensure floor 9 is always a treasure room
    for node in game_map[8]:
        node["type"] = "treasure"

    # Ensure floor 15 is boss (already done)

    # Enforce rules:
    # - Rest site on floor 14 (before boss)
    for node in game_map[13]:
        if random.random() < 0.5:
            node["type"] = "rest"

    return game_map


def _get_node_type(row, act):
    """Determine node type based on floor and act rules."""
    # Rules from the game:
    # Floor 1: always monster
    # Floor 9: always treasure
    # Floor 15: always boss
    # Elites: not on floors 1-4, weighted higher on later floors
    # Rest: not on floor 1, more common later
    # Shop: appears ~2 times per act

    roll = random.random()

    if row <= 3:
        # Early floors: mostly monsters and events
        if roll < 0.55:
            return "monster"
        elif roll < 0.80:
            return "event"
        elif roll < 0.95:
            return "monster"
        else:
            return "shop"

    elif row <= 6:
        # Mid floors: mix of everything
        if roll < 0.35:
            return "monster"
        elif roll < 0.55:
            return "event"
        elif roll < 0.70:
            return "elite"
        elif roll < 0.85:
            return "rest"
        else:
            return "shop"

    elif row <= 10:
        # Later floors: more elites and rest
        if roll < 0.30:
            return "monster"
        elif roll < 0.50:
            return "event"
        elif roll < 0.70:
            return "elite"
        elif roll < 0.90:
            return "rest"
        else:
            return "shop"

    else:
        # Final floors before boss
        if roll < 0.25:
            return "monster"
        elif roll < 0.45:
            return "event"
        elif roll < 0.60:
            return "elite"
        elif roll < 0.85:
            return "rest"
        else:
            return "shop"


def get_reachable_nodes(game_map, current_row, current_col):
    """Get list of nodes the player can move to from current position.
    If current_row is -1, return starting nodes (floor 0)."""
    if current_row == -1:
        return game_map[0]

    current_node = None
    for node in game_map[current_row]:
        if node["col"] == current_col:
            current_node = node
            break

    if not current_node:
        return []

    reachable = []
    for (r, c) in current_node["connections"]:
        for node in game_map[r]:
            if node["col"] == c:
                reachable.append(node)
                break
    return reachable


def display_map_text(game_map, current_row=-1):
    """Display map as text."""
    node_symbols = {
        "monster": "M", "elite": "E", "rest": "R",
        "shop": "$", "event": "?", "treasure": "T", "boss": "B",
    }

    print()
    for row in range(len(game_map) - 1, -1, -1):
        row_nodes = game_map[row]
        line = f"  F{row + 1:2d} "
        for col in range(7):
            found = False
            for node in row_nodes:
                if node["col"] == col:
                    symbol = node_symbols.get(node["type"], "?")
                    if node["visited"]:
                        line += f" . "
                    elif row == current_row + 1:  # next reachable row
                        line += f"[{symbol}]"
                    else:
                        line += f" {symbol} "
                    found = True
                    break
            if not found:
                line += "   "
        print(line)
    print()
