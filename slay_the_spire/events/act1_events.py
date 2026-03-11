"""Act 1 events - events specific to the first act."""
import random

from slay_the_spire import ui
from slay_the_spire.card import create_card, get_cards_by_color, CardColor
from slay_the_spire.events.shared_events import _get_player_color, _offer_card_removal, _get_random_curse


# =============================================================================
#  Act 1 Events
# =============================================================================

def event_screaming_skull(player):
    """Screaming Skull: gain gold or take damage."""
    gold_amount = random.randint(30, 50)
    damage = random.randint(6, 10)
    choices = [
        f"Smash the skull (gain {gold_amount} gold)",
        f"Run away (take {damage} damage)",
        "Leave quietly",
    ]
    ui.display_event(
        "Screaming Skull",
        "A skull mounted on a stake begins to scream as you approach.\n"
        "Its hollow eyes glow with an eerie light.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold += gold_amount
        print(f"  You smash the skull and find {gold_amount} gold inside!")
    elif choice == 1:
        player.lose_hp(damage)
        print(f"  You flee in terror! Took {damage} damage. (HP: {player.hp}/{player.max_hp})")
    else:
        print("  You tiptoe past the skull.")
    ui.press_enter()


def event_golden_wing(player):
    """Golden Wing: lose HP for gold, or gain nothing."""
    hp_cost = random.randint(5, 10)
    gold_gain = hp_cost * 10
    choices = [
        f"Pluck a feather (lose {hp_cost} HP, gain {gold_gain} gold)",
        "Admire and leave",
    ]
    ui.display_event(
        "Golden Wing",
        "A magnificent golden bird roosts on a high ledge.\n"
        "Its feathers shimmer with pure gold.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        if player.hp > hp_cost:
            player.lose_hp(hp_cost)
            player.gold += gold_gain
            print(f"  You pluck a feather! Lost {hp_cost} HP, gained {gold_gain} gold. (HP: {player.hp}/{player.max_hp})")
        else:
            print("  You're too weak to risk it. Nothing happens.")
    else:
        print("  You admire the golden bird and move on.")
    ui.press_enter()


def event_large_stump(player):
    """Large Stump: gain a random card."""
    ui.display_event(
        "Large Stump",
        "A large, ancient tree stump sits in the middle of the path.\n"
        "Something glows faintly inside a hollow in the stump.",
        ["Reach inside", "Leave"],
    )
    choice = ui.get_choice("What do you choose?", ["Reach inside", "Leave"])
    if choice == 0:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        if pool:
            card = create_card(random.choice(pool))
            player.add_card_to_deck(card)
            print(f"  You find a card: {card.name}!")
        else:
            player.gold += 20
            print("  You find 20 gold in the stump!")
    else:
        print("  You leave the stump alone.")
    ui.press_enter()


def event_mushrooms(player):
    """Mushrooms: fight fungi or leave. Gain 2 cards if you stay."""
    choices = [
        "Stomp the mushrooms (gain 2 random cards)",
        "Eat a mushroom (heal 25% HP)",
        "Leave",
    ]
    ui.display_event(
        "Mushrooms",
        "A cluster of enormous, colorful mushrooms grows along the path.\n"
        "Some look edible... others look dangerous.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        for _ in range(2):
            if pool:
                card = create_card(random.choice(pool))
                player.add_card_to_deck(card)
                print(f"  Gained: {card.name}!")
    elif choice == 1:
        heal_amount = max(1, int(player.max_hp * 0.25))
        healed = player.heal(heal_amount)
        print(f"  The mushroom tastes strange but heals you. Restored {healed} HP!")
    else:
        print("  You carefully walk around the mushrooms.")
    ui.press_enter()


def event_the_ssssserpent(player):
    """The Ssssserpent: gain 150 gold + Doubt curse, or decline."""
    choices = [
        "[Accept] Gain 150 gold (receive Doubt curse)",
        "[Decline] Refuse the offer",
    ]
    ui.display_event(
        "The Ssssserpent",
        "A hooded figure blocks your path, its tongue flicking.\n"
        "\"I have a gift for you... jussst take it. No ssstrings attached.\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold += 150
        try:
            doubt = create_card("doubt")
            player.add_card_to_deck(doubt)
            print("  Gained 150 gold! But the Doubt curse slithers into your deck...")
        except ValueError:
            curse = _get_random_curse()
            player.add_card_to_deck(curse)
            print(f"  Gained 150 gold! But gained {curse.name}...")
    else:
        print("  \"Your lossss...\" The serpent slithers away.")
    ui.press_enter()


def event_wing_statue(player):
    """Wing Statue: purify (remove a card) for 7 HP."""
    choices = [
        "Pray (lose 7 HP, remove a card)",
        "Leave",
    ]
    ui.display_event(
        "Wing Statue",
        "A winged statue stands in a clearing, radiating a purifying aura.\n"
        "It seems to demand a blood offering.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        if player.hp > 7:
            player.lose_hp(7)
            print(f"  You offer your blood. Lost 7 HP. (HP: {player.hp}/{player.max_hp})")
            _offer_card_removal(player)
        else:
            print("  You're too weak to make the offering.")
    else:
        print("  You leave the statue behind.")
    ui.press_enter()


# =============================================================================
#  Event list
# =============================================================================

def get_act1_events():
    """Return list of all Act 1 event functions."""
    return [
        event_screaming_skull,
        event_golden_wing,
        event_large_stump,
        event_mushrooms,
        event_the_ssssserpent,
        event_wing_statue,
    ]
