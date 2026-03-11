"""Act 2 events - events specific to the second act."""
import random

from slay_the_spire import ui
from slay_the_spire.card import create_card, get_cards_by_color, CardColor, CardType
from slay_the_spire.relic import create_relic, get_random_relic
from slay_the_spire.events.shared_events import (
    _get_player_color, _offer_card_removal, _offer_card_transform,
    _get_random_curse,
)


# =============================================================================
#  Act 2 Events
# =============================================================================

def event_ancient_writing(player):
    """Ancient Writing: upgrade all Strikes/Defends, or remove a card."""
    choices = [
        "[Elegance] Upgrade all Strikes and Defends",
        "[Simplicity] Remove a card from your deck",
    ]
    ui.display_event(
        "Ancient Writing",
        "You discover ancient writing carved into the walls.\n"
        "The text describes techniques for refining basic combat forms.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        upgraded_count = 0
        for card in player.deck:
            if card.name in ("Strike", "Defend") and not card.upgraded:
                card.upgrade()
                upgraded_count += 1
        # Also check for class-specific names
        for card in player.deck:
            base_name = card.name.rstrip("+")
            if base_name in ("Strike", "Defend") and not card.upgraded:
                card.upgrade()
                upgraded_count += 1
        print(f"  Upgraded {upgraded_count} basic card(s)!")
    elif choice == 1:
        _offer_card_removal(player)
    ui.press_enter()


def event_augmenter(player):
    """Augmenter: transform a card or gain Mutagenic Strength."""
    choices = [
        "Transform a card",
        "Gain Mutagenic Strength (random card + random upgrade)",
        "Leave",
    ]
    ui.display_event(
        "Augmenter",
        "A cloaked figure hunches over a bubbling cauldron.\n"
        "\"Step closer... I can change you. Make you stronger.\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        _offer_card_transform(player)
    elif choice == 1:
        color = _get_player_color(player)
        pool = get_cards_by_color(color)
        if pool:
            card = create_card(random.choice(pool))
            card.upgrade()
            player.add_card_to_deck(card)
            print(f"  Gained upgraded: {card.name}!")
        else:
            print("  The augmentation fizzles.")
    else:
        print("  You back away from the cauldron.")
    ui.press_enter()


def event_colosseum(player):
    """Colosseum: fight for gold or gain a relic."""
    choices = [
        "Fight in the arena (gain 75-125 gold, take damage)",
        "Bribe the guards (pay 50 gold, gain a relic)",
        "Leave",
    ]
    ui.display_event(
        "Colosseum",
        "You enter a massive colosseum. The crowd roars with excitement.\n"
        "\"Fight for glory, or pay for a shortcut!\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        damage = random.randint(10, 20)
        gold = random.randint(75, 125)
        player.lose_hp(damage)
        player.gold += gold
        print(f"  You battle through the arena! Took {damage} damage, gained {gold} gold. (HP: {player.hp}/{player.max_hp})")
    elif choice == 1:
        if player.gold >= 50:
            player.gold -= 50
            relic = get_random_relic()
            if relic:
                player.add_relic(relic)
                print(f"  Paid 50 gold. The guards hand you: {relic.name}!")
            else:
                print("  Paid 50 gold, but the guards had nothing worthwhile.")
        else:
            print("  You don't have enough gold to bribe the guards.")
    else:
        print("  You leave the colosseum.")
    ui.press_enter()


def event_council_of_ghosts(player):
    """Council of Ghosts: gain 5 Apparition cards + lose half HP."""
    half_hp = player.hp // 2
    choices = [
        f"[Accept] Gain 5 Apparitions, lose {half_hp} HP",
        "[Refuse] Leave",
    ]
    ui.display_event(
        "Council of Ghosts",
        "Ghostly figures materialize around you, whispering in unison.\n"
        "\"Accept our gift... become one with the ethereal...\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.lose_hp(half_hp)
        print(f"  Lost {half_hp} HP! (HP: {player.hp}/{player.max_hp})")
        for _ in range(5):
            try:
                apparition = create_card("apparition")
                player.add_card_to_deck(apparition)
            except ValueError:
                # Apparition card not registered; create a placeholder description
                from slay_the_spire.card import Card, CardType, CardRarity, CardColor, CardTarget
                apparition = Card(
                    "apparition", "Apparition", 1, CardType.SKILL, CardRarity.SPECIAL, CardColor.COLORLESS,
                    target=CardTarget.SELF,
                    description="Ethereal. Prevent ALL damage for 1 turn. Exhaust.",
                    ethereal=True, exhaust=True,
                    effects=[{"action": "custom", "func": "apparition_intangible"}],
                )
                player.add_card_to_deck(apparition)
        print("  Gained 5 Apparitions! (Ethereal - prevent all damage for 1 turn each)")
    else:
        print("  You refuse the ghosts' offer.")
    ui.press_enter()


def event_cursed_tome(player):
    """Cursed Tome: gain a random relic + 1 curse."""
    choices = [
        "Read the tome (gain a relic + a curse)",
        "Leave",
    ]
    ui.display_event(
        "Cursed Tome",
        "A heavy tome sits on a pedestal, its pages rustling on their own.\n"
        "Dark energy seeps from its binding.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  Gained relic: {relic.name}!")
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  The tome curses you! Gained {curse.name}.")
    else:
        print("  You leave the tome untouched.")
    ui.press_enter()


def event_forgotten_altar(player):
    """Forgotten Altar: sacrifice max HP for relic, or use Golden Idol."""
    has_golden_idol = player.has_relic("Golden Idol")
    choices = [
        "Sacrifice (lose 5 Max HP, gain a relic)",
    ]
    if has_golden_idol:
        choices.append("Offer Golden Idol (trade for Bloody Idol)")
    choices.append("Leave")

    ui.display_event(
        "Forgotten Altar",
        "A blood-stained altar stands before you.\n"
        "Ancient runes demand a sacrifice.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.max_hp -= 5
        player.hp = min(player.hp, player.max_hp)
        print(f"  Lost 5 Max HP! (HP: {player.hp}/{player.max_hp})")
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  The altar rewards you: {relic.name}!")
    elif choice == 1 and has_golden_idol:
        # Remove Golden Idol, gain Bloody Idol
        for i, r in enumerate(player.relics):
            if r.name == "Golden Idol":
                player.relics.pop(i)
                break
        try:
            bloody_idol = create_relic("bloody_idol")
            player.add_relic(bloody_idol)
            print("  Traded Golden Idol for Bloody Idol!")
        except (ValueError, KeyError):
            relic = get_random_relic()
            if relic:
                player.add_relic(relic)
                print(f"  Traded Golden Idol for {relic.name}!")
    else:
        print("  You leave the altar undisturbed.")
    ui.press_enter()


def event_ghosts(player):
    """Ghosts: gain Apparition cards + lose HP."""
    hp_cost = max(1, player.hp // 2)
    choices = [
        f"Accept (gain 3 Apparitions, lose {hp_cost} HP)",
        "Refuse",
    ]
    ui.display_event(
        "Ghosts",
        "Translucent spirits swirl around you, moaning softly.\n"
        "They offer ethereal protection in exchange for life force.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.lose_hp(hp_cost)
        print(f"  Lost {hp_cost} HP! (HP: {player.hp}/{player.max_hp})")
        for _ in range(3):
            try:
                apparition = create_card("apparition")
                player.add_card_to_deck(apparition)
            except ValueError:
                from slay_the_spire.card import Card, CardType, CardRarity, CardColor, CardTarget
                apparition = Card(
                    "apparition", "Apparition", 1, CardType.SKILL, CardRarity.SPECIAL, CardColor.COLORLESS,
                    target=CardTarget.SELF,
                    description="Ethereal. Prevent ALL damage for 1 turn. Exhaust.",
                    ethereal=True, exhaust=True,
                    effects=[{"action": "custom", "func": "apparition_intangible"}],
                )
                player.add_card_to_deck(apparition)
        print("  Gained 3 Apparitions!")
    else:
        print("  The spirits drift away, disappointed.")
    ui.press_enter()


def event_masked_bandits(player):
    """Masked Bandits: lose all gold or fight."""
    choices = [
        f"Pay up (lose all {player.gold} gold)",
        "Fight! (take 15 damage, keep your gold)",
    ]
    ui.display_event(
        "Masked Bandits",
        "A group of masked bandits surrounds you.\n"
        "\"Your gold or your life!\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        lost = player.gold
        player.gold = 0
        print(f"  You hand over {lost} gold. The bandits vanish into the shadows.")
    elif choice == 1:
        damage = 15
        player.lose_hp(damage)
        print(f"  You fight off the bandits! Took {damage} damage. (HP: {player.hp}/{player.max_hp})")
        bonus_gold = random.randint(20, 40)
        player.gold += bonus_gold
        print(f"  You loot {bonus_gold} gold from the defeated bandits!")
    ui.press_enter()


def event_the_mausoleum(player):
    """The Mausoleum: open coffin for relic + curse, or leave."""
    choices = [
        "Open the coffin (gain a relic, may gain a curse)",
        "Leave",
    ]
    ui.display_event(
        "The Mausoleum",
        "You enter a dusty mausoleum. An ornate coffin sits in the center.\n"
        "Something glints inside through a crack in the lid.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  Obtained: {relic.name}!")
        if random.random() < 0.5:
            curse = _get_random_curse()
            player.add_card_to_deck(curse)
            print(f"  A dark energy escapes! Gained {curse.name}.")
        else:
            print("  The coffin closes peacefully behind you.")
    else:
        print("  You leave the mausoleum undisturbed.")
    ui.press_enter()


def event_mysterious_sphere(player):
    """Mysterious Sphere: open for relic (with damage) or leave."""
    choices = [
        "Open the sphere (take 15-25 damage, gain a relic)",
        "Leave",
    ]
    ui.display_event(
        "Mysterious Sphere",
        "A glowing sphere hovers in the center of the room.\n"
        "It crackles with unstable energy, but you sense something valuable inside.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        damage = random.randint(15, 25)
        player.lose_hp(damage)
        print(f"  The sphere explodes! Took {damage} damage. (HP: {player.hp}/{player.max_hp})")
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  From the debris you recover: {relic.name}!")
    else:
        print("  You back away from the unstable sphere.")
    ui.press_enter()


def event_the_joust(player):
    """The Joust: bet on a fighter (50/50 win/lose gold)."""
    bet = 50
    choices = [
        f"Bet on the Red Knight ({bet} gold, 50/50)",
        f"Bet on the Blue Knight ({bet} gold, 50/50)",
        "Don't bet",
    ]
    ui.display_event(
        "The Joust",
        "Two knights prepare to joust in a grand arena.\n"
        "A bookie approaches you. \"Care to place a wager?\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice in (0, 1):
        if player.gold >= bet:
            player.gold -= bet
            if random.random() < 0.5:
                winnings = bet * 3
                player.gold += winnings
                knight = "Red" if choice == 0 else "Blue"
                print(f"  The {knight} Knight wins! You gain {winnings} gold!")
            else:
                knight = "Red" if choice == 0 else "Blue"
                print(f"  The {knight} Knight loses! You lost {bet} gold.")
        else:
            print("  You don't have enough gold to bet.")
    else:
        print("  You watch the joust without betting.")
    ui.press_enter()


def event_vampire_lair(player):
    """Vampire Lair: lose all Strikes, gain Bites, or lose HP."""
    strike_count = sum(1 for c in player.deck if c.name.startswith("Strike"))
    choices = [
        f"[Accept] Lose {strike_count} Strike(s), gain {max(strike_count, 1)} Bite(s)",
        "Refuse (lose 10 HP)",
    ]
    ui.display_event(
        "Vampire Lair",
        "You stumble into a vampire's lair. Crimson eyes stare from the darkness.\n"
        "\"Join us... exchange your crude strikes for something more... refined.\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        # Remove all Strikes
        new_deck = []
        removed = 0
        for c in player.deck:
            if c.name.startswith("Strike"):
                removed += 1
            else:
                new_deck.append(c)
        player.deck = new_deck
        print(f"  Removed {removed} Strike(s).")
        # Gain Bites
        bite_count = max(removed, 1)
        for _ in range(bite_count):
            try:
                bite = create_card("bite")
                player.add_card_to_deck(bite)
            except ValueError:
                from slay_the_spire.card import Card, CardType, CardRarity, CardColor, CardTarget
                bite = Card(
                    "bite", "Bite", 1, CardType.ATTACK, CardRarity.SPECIAL, CardColor.COLORLESS,
                    target=CardTarget.ENEMY,
                    description="Deal 7 damage. Heal 2 HP.",
                    base_damage=7,
                    effects=[{"action": "heal", "amount": 2}],
                )
                player.add_card_to_deck(bite)
        print(f"  Gained {bite_count} Bite(s)! (1 cost, 7 damage, heal 2 HP)")
    elif choice == 1:
        player.lose_hp(10)
        print(f"  The vampires attack as you flee! Lost 10 HP. (HP: {player.hp}/{player.max_hp})")
    ui.press_enter()


# =============================================================================
#  Event list
# =============================================================================

def get_act2_events():
    """Return list of all Act 2 event functions."""
    return [
        event_ancient_writing,
        event_augmenter,
        event_colosseum,
        event_council_of_ghosts,
        event_cursed_tome,
        event_forgotten_altar,
        event_ghosts,
        event_masked_bandits,
        event_the_mausoleum,
        event_mysterious_sphere,
        event_the_joust,
        event_vampire_lair,
    ]
