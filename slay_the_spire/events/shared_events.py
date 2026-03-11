"""Shared events that can appear in multiple acts."""
import random

from slay_the_spire import ui
from slay_the_spire.card import create_card, get_all_card_ids, get_cards_by_color, CardColor, CardType, CardRarity
from slay_the_spire.relic import create_relic, get_random_relic
from slay_the_spire.potion import get_random_potion


# =============================================================================
#  Helper utilities
# =============================================================================

def _get_random_curse():
    """Return a random curse card."""
    curses = ["doubt", "pain", "parasite", "regret", "shame", "injury", "decay", "normality", "writhe", "clumsy"]
    return create_card(random.choice(curses))


def _get_player_color(player):
    """Map character class to CardColor."""
    mapping = {
        "ironclad": CardColor.RED,
        "silent": CardColor.GREEN,
        "defect": CardColor.BLUE,
        "watcher": CardColor.PURPLE,
    }
    return mapping.get(player.character_class, CardColor.RED)


def _offer_card_removal(player):
    """Let the player choose a card to remove from their deck."""
    if not player.deck:
        print("  You have no cards to remove.")
        return False
    options = [f"{c.name} [{c.card_type.name}]" for c in player.deck]
    choice = ui.get_choice("Choose a card to remove:", options, allow_cancel=True, cancel_text="Cancel")
    if choice == -1:
        return False
    removed = player.deck.pop(choice)
    print(f"  Removed {removed.name} from your deck.")
    return True


def _offer_card_transform(player):
    """Let the player choose a card to transform (replace with random card of same type)."""
    if not player.deck:
        print("  You have no cards to transform.")
        return False
    options = [f"{c.name} [{c.card_type.name}]" for c in player.deck]
    choice = ui.get_choice("Choose a card to transform:", options, allow_cancel=True, cancel_text="Cancel")
    if choice == -1:
        return False
    old_card = player.deck.pop(choice)
    color = _get_player_color(player)
    pool = get_cards_by_color(color)
    if pool:
        new_id = random.choice(pool)
        new_card = create_card(new_id)
        player.deck.append(new_card)
        print(f"  {old_card.name} transformed into {new_card.name}!")
    else:
        player.deck.append(old_card)
        print("  The transformation fizzles...")
    return True


def _offer_card_upgrade(player):
    """Let the player choose a card to upgrade."""
    upgradable = [(i, c) for i, c in enumerate(player.deck) if not c.upgraded]
    if not upgradable:
        print("  You have no cards to upgrade.")
        return False
    options = [f"{c.name} [{c.card_type.name}]" for _, c in upgradable]
    choice = ui.get_choice("Choose a card to upgrade:", options, allow_cancel=True, cancel_text="Cancel")
    if choice == -1:
        return False
    idx, card = upgradable[choice]
    card.upgrade()
    print(f"  Upgraded {card.name}!")
    return True


# =============================================================================
#  Events
# =============================================================================

def event_big_fish(player):
    """Big Fish: choose Banana (heal), Donut (max HP), or Box (relic + curse)."""
    choices = [
        "[Banana] Heal 5 HP",
        "[Donut] Max HP +5",
        "[Box] Obtain a relic, but receive a Curse",
    ]
    ui.display_event(
        "Big Fish",
        "You come across a big fish flopping on the bank of a river.\n"
        "It offers you a gift in exchange for helping it back into the water.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        healed = player.heal(5)
        print(f"  You eat the Banana. Healed {healed} HP!")
    elif choice == 1:
        player.max_hp += 5
        player.hp += 5
        print("  You eat the Donut. Max HP increased by 5!")
    elif choice == 2:
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  You open the Box and find: {relic.name}!")
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  A {curse.name} was added to your deck.")
    ui.press_enter()


def event_the_cleric(player):
    """The Cleric: pay gold to heal or remove a card."""
    choices = [
        "[Heal] Pay 35 gold, heal 25% HP",
        "[Purify] Pay 50 gold, remove a card",
        "Leave",
    ]
    ui.display_event(
        "The Cleric",
        "A cleric in white robes beckons you toward a makeshift altar.\n"
        "\"I can mend your wounds or cleanse your burdens... for a price.\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        if player.gold >= 35:
            player.gold -= 35
            heal_amount = max(1, int(player.max_hp * 0.25))
            healed = player.heal(heal_amount)
            print(f"  Paid 35 gold. Healed {healed} HP!")
        else:
            print("  You don't have enough gold.")
    elif choice == 1:
        if player.gold >= 50:
            player.gold -= 50
            _offer_card_removal(player)
        else:
            print("  You don't have enough gold.")
    else:
        print("  You leave the cleric in peace.")
    ui.press_enter()


def event_dead_adventurer(player):
    """Dead Adventurer: search the body or leave."""
    choices = [
        "Search the body",
        "Leave",
    ]
    ui.display_event(
        "Dead Adventurer",
        "You discover the remains of an unfortunate adventurer.\n"
        "Their pack might contain something useful... or something sinister.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        roll = random.random()
        if roll < 0.40:
            relic = get_random_relic()
            if relic:
                player.add_relic(relic)
                print(f"  You found a relic: {relic.name}!")
            else:
                player.gold += 30
                print("  You found 30 gold!")
        elif roll < 0.70:
            curse = _get_random_curse()
            player.add_card_to_deck(curse)
            print(f"  Something dark attaches itself to you... gained {curse.name}.")
        else:
            damage = random.randint(6, 12)
            player.lose_hp(damage)
            print(f"  A trap! You take {damage} damage! (HP: {player.hp}/{player.max_hp})")
    else:
        print("  You leave the body undisturbed.")
    ui.press_enter()


def event_golden_shrine(player):
    """Golden Shrine: gain gold, possibly with a curse."""
    choices = [
        "Pray for gold (gain 100 gold)",
        "Desecrate (gain 50 gold, receive a Curse)",
        "Leave",
    ]
    ui.display_event(
        "Golden Shrine",
        "A golden shrine glows softly in the dim passage.\n"
        "You feel its power radiating outward.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold += 100
        print("  You pray and receive 100 gold!")
    elif choice == 1:
        player.gold += 50
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  You desecrate the shrine. Gained 50 gold and {curse.name}.")
    else:
        print("  You leave the shrine untouched.")
    ui.press_enter()


def event_lab(player):
    """Lab: obtain 3 random potions."""
    ui.display_event(
        "Lab",
        "You stumble into an abandoned alchemist's laboratory.\n"
        "Shelves of potions line the walls, still intact.",
        ["Take the potions"],
    )
    ui.get_choice("What do you choose?", ["Take the potions"])
    potions_obtained = 0
    for _ in range(3):
        potion = get_random_potion()
        if player.add_potion(potion):
            print(f"  Obtained: {potion.name}!")
            potions_obtained += 1
        else:
            print(f"  No room for {potion.name}. Discarded.")
    if potions_obtained == 0:
        print("  Your potion belt is full!")
    ui.press_enter()


def event_match_and_keep(player):
    """Match and Keep: simplified memory game - gain cards."""
    ui.display_event(
        "Match and Keep",
        "A ghostly figure presents a card game.\n"
        "\"Match the pairs and keep what you find...\"",
        ["Play the game", "Leave"],
    )
    choice = ui.get_choice("What do you choose?", ["Play the game", "Leave"])
    if choice == 0:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        pairs_found = random.randint(1, 3)
        print(f"  You matched {pairs_found} pair(s)!")
        for _ in range(pairs_found):
            if pool:
                card_id = random.choice(pool)
                card = create_card(card_id)
                player.add_card_to_deck(card)
                print(f"  Gained: {card.name}!")
    else:
        print("  You walk away from the game.")
    ui.press_enter()


def event_bonfire_spirits(player):
    """Bonfire Spirits: offer (remove) a card. If rare, gain a relic."""
    ui.display_event(
        "Bonfire Spirits",
        "Ethereal spirits dance around a bonfire.\n"
        "They seem to want an offering...",
        ["Offer a card", "Leave"],
    )
    choice = ui.get_choice("What do you choose?", ["Offer a card", "Leave"])
    if choice == 0:
        if not player.deck:
            print("  You have no cards to offer.")
        else:
            options = [f"{c.name} [{c.card_type.name}] ({c.rarity.name})" for c in player.deck]
            card_choice = ui.get_choice("Choose a card to offer:", options, allow_cancel=True, cancel_text="Cancel")
            if card_choice != -1:
                removed = player.deck.pop(card_choice)
                print(f"  You offer {removed.name} to the flames.")
                if removed.rarity == CardRarity.RARE:
                    relic = get_random_relic()
                    if relic:
                        player.add_relic(relic)
                        print(f"  The spirits are pleased! You receive: {relic.name}!")
                else:
                    print("  The spirits accept your offering.")
    else:
        print("  You leave the spirits to their dance.")
    ui.press_enter()


def event_knowing_skull(player):
    """Knowing Skull: buy HP, gold, cards, or potions at HP cost."""
    ui.display_event(
        "Knowing Skull",
        "A massive skull floats before you, its hollow eyes glowing.\n"
        "\"I can grant you many things... but everything has a price. YOUR price.\"",
        [
            f"A potion... (Lose ~10 HP, currently {player.hp})",
            f"Gold... (Lose ~10 HP, gain 90 gold)",
            f"A card... (Lose ~10 HP)",
            "Leave",
        ],
    )
    while True:
        options = [
            f"A potion... (Lose ~10 HP, currently {player.hp})",
            f"Gold... (Lose ~10 HP, gain 90 gold)",
            f"A card... (Lose ~10 HP)",
            "Leave",
        ]
        choice = ui.get_choice("The skull awaits:", options)
        if choice == 0:
            cost = random.randint(8, 12)
            if player.hp <= cost:
                print("  \"You can't afford that with your life force...\"")
            else:
                player.lose_hp(cost)
                potion = get_random_potion()
                if player.add_potion(potion):
                    print(f"  Lost {cost} HP. Obtained: {potion.name}!")
                else:
                    print(f"  Lost {cost} HP, but no room for the potion!")
        elif choice == 1:
            cost = random.randint(8, 12)
            if player.hp <= cost:
                print("  \"You can't afford that with your life force...\"")
            else:
                player.lose_hp(cost)
                player.gold += 90
                print(f"  Lost {cost} HP. Gained 90 gold!")
        elif choice == 2:
            cost = random.randint(8, 12)
            if player.hp <= cost:
                print("  \"You can't afford that with your life force...\"")
            else:
                player.lose_hp(cost)
                color = _get_player_color(player)
                pool = get_cards_by_color(color)
                if pool:
                    card = create_card(random.choice(pool))
                    player.add_card_to_deck(card)
                    print(f"  Lost {cost} HP. Gained: {card.name}!")
                else:
                    print(f"  Lost {cost} HP, but the skull has nothing for you.")
        else:
            print("  \"Come back anytime...\" The skull fades away.")
            break
    ui.press_enter()


def event_the_woman_in_blue(player):
    """The Woman in Blue: buy 1-3 potions for gold."""
    potion1 = get_random_potion()
    potion2 = get_random_potion()
    potion3 = get_random_potion()
    potions = [potion1, potion2, potion3]
    price = 20

    ui.display_event(
        "The Woman in Blue",
        "A mysterious woman in a blue cloak approaches.\n"
        "She opens her bag to reveal an assortment of potions.",
        [
            f"Buy {potion1.name} ({price} gold)",
            f"Buy {potion2.name} ({price} gold)",
            f"Buy {potion3.name} ({price} gold)",
            "Leave",
        ],
    )
    while True:
        available = []
        for i, p in enumerate(potions):
            if p is not None:
                available.append(f"Buy {p.name} ({price} gold)")
            else:
                available.append(f"[Sold out]")
        available.append("Leave")
        choice = ui.get_choice("What do you choose?", available)
        if choice < 3 and potions[choice] is not None:
            if player.gold >= price:
                player.gold -= price
                if player.add_potion(potions[choice]):
                    print(f"  Purchased {potions[choice].name}!")
                else:
                    print(f"  No room for the potion! Gold refunded.")
                    player.gold += price
                potions[choice] = None
            else:
                print("  You don't have enough gold.")
        elif choice == 3 or choice == len(available) - 1:
            print("  You wave goodbye to the mysterious woman.")
            break
    ui.press_enter()


def event_world_of_goop(player):
    """World of Goop: gain gold and lose HP, or leave."""
    choices = [
        "Gather the gold (gain 75 gold, lose 11 HP)",
        "Leave it",
    ]
    ui.display_event(
        "World of Goop",
        "You find a pool of shimmering, acidic goop.\n"
        "Gold coins glitter at the bottom.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold += 75
        player.lose_hp(11)
        print(f"  You scoop out the gold! Gained 75 gold, lost 11 HP. (HP: {player.hp}/{player.max_hp})")
    else:
        print("  You leave the goop alone.")
    ui.press_enter()


def event_living_wall(player):
    """Living Wall: remove, transform, or upgrade a card."""
    choices = [
        "[Forget] Remove a card",
        "[Change] Transform a card",
        "[Grow] Upgrade a card",
    ]
    ui.display_event(
        "Living Wall",
        "The wall before you pulses with life.\n"
        "Three faces emerge from the stone, each offering a different gift.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        _offer_card_removal(player)
    elif choice == 1:
        _offer_card_transform(player)
    elif choice == 2:
        _offer_card_upgrade(player)
    ui.press_enter()


def event_scrap_ooze(player):
    """Scrap Ooze: repeatedly take 3 damage for a chance at a relic."""
    ui.display_event(
        "Scrap Ooze",
        "A massive ooze blocks the path, a relic glinting inside its body.\n"
        "You could try to reach in and grab it, but it won't be pleasant...",
        ["Reach inside", "Leave"],
    )
    choice = ui.get_choice("What do you choose?", ["Reach inside", "Leave"])
    if choice == 0:
        attempt = 0
        while True:
            attempt += 1
            player.lose_hp(3)
            print(f"  Attempt {attempt}: Took 3 damage! (HP: {player.hp}/{player.max_hp})")
            if player.hp <= 0:
                print("  You collapse from the ooze's acid...")
                break
            if random.random() < 0.75:
                relic = get_random_relic()
                if relic:
                    player.add_relic(relic)
                    print(f"  You wrench the relic free: {relic.name}!")
                break
            else:
                cont_choices = ["Reach in again", "Give up"]
                cont = ui.get_choice("The relic slips from your grasp!", cont_choices)
                if cont == 1:
                    print("  You give up and back away.")
                    break
    else:
        print("  You leave the ooze undisturbed.")
    ui.press_enter()


def event_shining_light(player):
    """Shining Light: upgrade 2 random cards, take damage equal to 20% max HP."""
    damage = max(1, int(player.max_hp * 0.20))
    ui.display_event(
        "Shining Light",
        "A blinding beam of light shines from an opening in the ceiling.\n"
        "You feel its power could improve your abilities, but at a cost.",
        [f"Step into the light (Upgrade 2 random cards, take {damage} damage)", "Leave"],
    )
    choice = ui.get_choice("What do you choose?",
                           [f"Step into the light (take {damage} damage)", "Leave"])
    if choice == 0:
        player.lose_hp(damage)
        print(f"  You step into the light. Took {damage} damage! (HP: {player.hp}/{player.max_hp})")
        upgradable = [c for c in player.deck if not c.upgraded]
        random.shuffle(upgradable)
        upgraded_count = 0
        for card in upgradable[:2]:
            card.upgrade()
            print(f"  Upgraded: {card.name}!")
            upgraded_count += 1
        if upgraded_count == 0:
            print("  No cards could be upgraded.")
    else:
        print("  You shield your eyes and walk away.")
    ui.press_enter()


def event_wheel_of_change(player):
    """Wheel of Change: spin the wheel for a random outcome."""
    ui.display_event(
        "Wheel of Change",
        "A great wheel stands before you, covered in strange symbols.\n"
        "\"Give it a spin!\" a voice echoes.",
        ["Spin the wheel"],
    )
    ui.get_choice("What do you choose?", ["Spin the wheel"])
    outcome = random.randint(1, 6)
    if outcome == 1:
        gold = random.randint(50, 150)
        player.gold += gold
        print(f"  The wheel stops on GOLD! Gained {gold} gold!")
    elif outcome == 2:
        heal_amount = max(1, int(player.max_hp * 0.25))
        healed = player.heal(heal_amount)
        print(f"  The wheel stops on HEAL! Restored {healed} HP!")
    elif outcome == 3:
        damage = random.randint(8, 15)
        player.lose_hp(damage)
        print(f"  The wheel stops on PAIN! Took {damage} damage! (HP: {player.hp}/{player.max_hp})")
    elif outcome == 4:
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  The wheel stops on CURSE! Gained {curse.name}.")
    elif outcome == 5:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        if pool:
            card = create_card(random.choice(pool))
            player.add_card_to_deck(card)
            print(f"  The wheel stops on CARD! Gained {card.name}!")
        else:
            player.gold += 50
            print("  The wheel stops on GOLD! Gained 50 gold!")
    elif outcome == 6:
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  The wheel stops on RELIC! Obtained {relic.name}!")
        else:
            player.gold += 100
            print("  The wheel stops on GOLD! Gained 100 gold!")
    ui.press_enter()


def event_nest(player):
    """Nest: gain gold + Ritual Dagger, or just gain gold."""
    choices = [
        "Grab the dagger and gold (99 gold + Ritual Dagger card)",
        "Take only the gold (99 gold)",
        "Leave",
    ]
    ui.display_event(
        "Nest",
        "You discover a large nest filled with gold and a strange dagger.\n"
        "The nest's owner is nowhere to be seen... for now.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold += 99
        try:
            dagger = create_card("ritual_dagger")
            player.add_card_to_deck(dagger)
            print("  Gained 99 gold and Ritual Dagger!")
        except ValueError:
            print("  Gained 99 gold! (Ritual Dagger not available)")
    elif choice == 1:
        player.gold += 99
        print("  Gained 99 gold!")
    else:
        print("  You leave the nest alone.")
    ui.press_enter()


def event_nloth(player):
    """N'loth: trade a relic for a random relic gift."""
    if not player.relics:
        ui.display_event(
            "N'loth",
            "A strange creature sits cross-legged, surrounded by trinkets.\n"
            "\"You have nothing to trade...\" it says sadly.",
            ["Leave"],
        )
        ui.get_choice("What do you choose?", ["Leave"])
        ui.press_enter()
        return

    choices = [f"Trade {r.name}" for r in player.relics]
    choices.append("Leave")
    ui.display_event(
        "N'loth",
        "A strange creature sits cross-legged, surrounded by trinkets.\n"
        "\"Trade me a trinket, and I'll give you something wonderful!\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice < len(player.relics):
        old_relic = player.relics.pop(choice)
        new_relic = get_random_relic(exclude={r.name for r in player.relics})
        if new_relic:
            player.add_relic(new_relic)
            print(f"  Traded {old_relic.name} for {new_relic.name}!")
        else:
            print(f"  Traded {old_relic.name}, but N'loth had nothing to give...")
    else:
        print("  You leave N'loth to its trinkets.")
    ui.press_enter()


def event_the_library(player):
    """The Library: choose from 20 cards or heal 20% max HP."""
    choices = [
        "Read (choose from a selection of cards)",
        "Sleep (heal 20% max HP)",
    ]
    ui.display_event(
        "The Library",
        "You discover an ancient library, its shelves overflowing with tomes.\n"
        "The musty air is thick with knowledge... or perhaps slumber.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        if pool:
            selection = random.sample(pool, min(20, len(pool)))
            card_options = []
            cards = []
            for cid in selection:
                c = create_card(cid)
                cards.append(c)
                card_options.append(f"[{c.get_display_cost()}] {c.name} ({c.rarity.name}) - {c.description}")
            card_choice = ui.get_choice("Choose a card to add:", card_options, allow_cancel=True, cancel_text="Take nothing")
            if card_choice != -1:
                player.add_card_to_deck(cards[card_choice])
                print(f"  Added {cards[card_choice].name} to your deck!")
            else:
                print("  You found nothing of interest.")
        else:
            print("  The shelves are bare.")
    else:
        heal_amount = max(1, int(player.max_hp * 0.20))
        healed = player.heal(heal_amount)
        print(f"  You take a nap among the books. Healed {healed} HP!")
    ui.press_enter()


def event_note_for_yourself(player):
    """Note for Yourself: gain a random card (simplified from cross-run mechanic)."""
    ui.display_event(
        "Note for Yourself",
        "You find a note pinned to the wall. The handwriting is yours!\n"
        "\"Take this, you'll need it. - Past You\"",
        ["Take the card"],
    )
    ui.get_choice("What do you choose?", ["Take the card"])
    color = _get_player_color(player)
    pool = get_cards_by_color(color)
    if pool:
        selection = random.sample(pool, min(3, len(pool)))
        card_options = []
        cards = []
        for cid in selection:
            c = create_card(cid)
            cards.append(c)
            card_options.append(f"[{c.get_display_cost()}] {c.name} ({c.rarity.name})")
        card_choice = ui.get_choice("Choose a card:", card_options, allow_cancel=True, cancel_text="Decline")
        if card_choice != -1:
            player.add_card_to_deck(cards[card_choice])
            print(f"  Gained {cards[card_choice].name}!")
        else:
            print("  You crumple the note and toss it aside.")
    else:
        player.gold += 25
        print("  The note crumbles. You find 25 gold behind it.")
    ui.press_enter()


def event_winding_halls(player):
    """Winding Halls: pick a direction with various effects."""
    choices = [
        "Go left (mysterious path)",
        "Go right (shadowy corridor)",
        "Go straight (dim passage)",
    ]
    ui.display_event(
        "Winding Halls",
        "The passage splits into three directions.\n"
        "Each path looks equally ominous.",
        choices,
    )
    choice = ui.get_choice("Which way?", choices)
    if choice == 0:
        # Curse
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        player.max_hp += 5
        player.hp += 5
        print(f"  You find dark power. Max HP +5, but gained {curse.name}.")
    elif choice == 1:
        # Damage + gold
        damage = random.randint(5, 10)
        gold = random.randint(30, 60)
        player.lose_hp(damage)
        player.gold += gold
        print(f"  A trap! Took {damage} damage but found {gold} gold. (HP: {player.hp}/{player.max_hp})")
    elif choice == 2:
        # Heal
        heal_amount = max(1, int(player.max_hp * 0.15))
        healed = player.heal(heal_amount)
        print(f"  A peaceful glade. Healed {healed} HP!")
    ui.press_enter()


# =============================================================================
#  Event list
# =============================================================================

def get_shared_events():
    """Return list of all shared event functions."""
    return [
        event_big_fish,
        event_the_cleric,
        event_dead_adventurer,
        event_golden_shrine,
        event_lab,
        event_match_and_keep,
        event_bonfire_spirits,
        event_knowing_skull,
        event_the_woman_in_blue,
        event_world_of_goop,
        event_living_wall,
        event_scrap_ooze,
        event_shining_light,
        event_wheel_of_change,
        event_nest,
        event_nloth,
        event_the_library,
        event_note_for_yourself,
        event_winding_halls,
    ]
