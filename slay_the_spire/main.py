"""Slay the Spire - Text-based CLI version.

Entry point for the game.  Run with:
    python -m slay_the_spire.main
"""

# --- Import card modules so they register themselves in the card registry ---
import slay_the_spire.cards.ironclad      # noqa: F401
import slay_the_spire.cards.silent        # noqa: F401
import slay_the_spire.cards.defect        # noqa: F401
import slay_the_spire.cards.watcher       # noqa: F401
import slay_the_spire.cards.colorless     # noqa: F401
import slay_the_spire.cards.curses        # noqa: F401
import slay_the_spire.cards.status        # noqa: F401

from slay_the_spire.player import Player
from slay_the_spire.card import create_card
from slay_the_spire.relic import create_relic
from slay_the_spire.game import Game
from slay_the_spire import ui


# =========================================================================
# Character definitions
# =========================================================================

CHARACTERS = {
    "ironclad": {
        "name": "Ironclad",
        "max_hp": 80,
        "relic": "burning_blood",
        "deck": [
            "ironclad_strike", "ironclad_strike", "ironclad_strike", "ironclad_strike", "ironclad_strike",
            "ironclad_defend", "ironclad_defend", "ironclad_defend", "ironclad_defend",
            "bash",
        ],
    },
    "silent": {
        "name": "Silent",
        "max_hp": 70,
        "relic": "ring_of_the_snake",
        "deck": [
            "silent_strike", "silent_strike", "silent_strike",
            "silent_strike", "silent_strike",
            "silent_defend", "silent_defend", "silent_defend",
            "silent_defend", "silent_defend",
            "survivor",
            "neutralize",
        ],
    },
    "defect": {
        "name": "Defect",
        "max_hp": 75,
        "relic": "cracked_core",
        "deck": [
            "defect_strike", "defect_strike", "defect_strike", "defect_strike",
            "defect_defend", "defect_defend", "defect_defend", "defect_defend",
            "zap",
            "dualcast",
        ],
    },
    "watcher": {
        "name": "Watcher",
        "max_hp": 72,
        "relic": "pure_water",
        "deck": [
            "watcher_strike", "watcher_strike", "watcher_strike", "watcher_strike",
            "watcher_defend", "watcher_defend", "watcher_defend", "watcher_defend",
            "eruption",
            "vigilance",
        ],
    },
}


# =========================================================================
# Welcome & character selection
# =========================================================================

def display_welcome():
    """Show the title screen."""
    ui.clear_screen()
    print()
    print("=" * 60)
    print()
    print("      ____  _             _   _            ____        _")
    print("     / ___|| | __ _ _   _| |_| |__   ___  / ___| _ __ (_)_ __ ___")
    print("     \\___ \\| |/ _` | | | | __| '_ \\ / _ \\ \\___ \\| '_ \\| | '__/ _ \\")
    print("      ___) | | (_| | |_| | |_| | | |  __/  ___) | |_) | | | |  __/")
    print("     |____/|_|\\__,_|\\__, |\\__|_| |_|\\___| |____/| .__/|_|_|  \\___|")
    print("                    |___/                        |_|")
    print()
    print("              T E X T - B A S E D    A D V E N T U R E")
    print()
    print("=" * 60)
    print()


def select_character():
    """Let the player choose a character class."""
    print("  Choose your character:\n")
    entries = list(CHARACTERS.items())
    options = []
    for key, cfg in entries:
        options.append(f"{cfg['name']} (HP: {cfg['max_hp']})")
    idx = ui.get_choice("", options)
    return entries[idx][0]  # return the key


def build_player(char_key):
    """Construct a Player with the chosen character's starter config."""
    cfg = CHARACTERS[char_key]
    player = Player(
        name=cfg["name"],
        max_hp=cfg["max_hp"],
        character_class=char_key,
    )

    # Add starter relic
    starter_relic = create_relic(cfg["relic"])
    player.add_relic(starter_relic)

    # Build starter deck
    for card_id in cfg["deck"]:
        card = create_card(card_id)
        player.add_card_to_deck(card)

    return player


# =========================================================================
# Main
# =========================================================================

def main():
    display_welcome()
    ui.press_enter()

    char_key = select_character()
    player = build_player(char_key)

    ui.clear_screen()
    print()
    ui.print_header(f"Starting run as {player.name}")
    print(f"\n  HP: {player.hp}/{player.max_hp}")
    print(f"  Starter relic: {player.relics[0].name}")
    print(f"  Deck size: {len(player.deck)} cards")
    print()
    ui.press_enter()

    game = Game(player)
    game.run()


if __name__ == "__main__":
    main()
