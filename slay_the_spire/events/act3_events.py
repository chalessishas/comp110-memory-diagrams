"""Act 3 events - events specific to the third act."""
import random

from slay_the_spire import ui
from slay_the_spire.card import (
    create_card, get_cards_by_color, CardColor, CardType, CardRarity,
)
from slay_the_spire.relic import get_random_relic, RelicRarity
from slay_the_spire.events.shared_events import _get_player_color, _get_random_curse


# =============================================================================
#  Act 3 Events
# =============================================================================

def event_falling(player):
    """Falling: choose a card to lose (Skill, Power, or Attack)."""
    skills = [c for c in player.deck if c.card_type == CardType.SKILL]
    powers = [c for c in player.deck if c.card_type == CardType.POWER]
    attacks = [c for c in player.deck if c.card_type == CardType.ATTACK]

    choices = []
    choice_map = []
    if skills:
        random_skill = random.choice(skills)
        choices.append(f"Lose a Skill: {random_skill.name}")
        choice_map.append(("skill", random_skill))
    if powers:
        random_power = random.choice(powers)
        choices.append(f"Lose a Power: {random_power.name}")
        choice_map.append(("power", random_power))
    if attacks:
        random_attack = random.choice(attacks)
        choices.append(f"Lose an Attack: {random_attack.name}")
        choice_map.append(("attack", random_attack))

    if not choices:
        ui.display_event(
            "Falling",
            "You feel yourself falling through darkness.\n"
            "But you have nothing to lose...",
            ["Continue"],
        )
        ui.get_choice("What do you choose?", ["Continue"])
        ui.press_enter()
        return

    ui.display_event(
        "Falling",
        "You feel yourself falling through darkness.\n"
        "Something must be left behind to stop the descent.",
        choices,
    )
    choice = ui.get_choice("What do you sacrifice?", choices)
    if 0 <= choice < len(choice_map):
        card_type, card = choice_map[choice]
        if card in player.deck:
            player.deck.remove(card)
            print(f"  {card.name} fades into the darkness...")
    ui.press_enter()


def event_mind_bloom(player):
    """Mind Bloom: fight Act 1 boss for rare relic, upgrade all cards, or gain 999 gold."""
    choices = [
        "[I am War] Fight an Act 1 boss for a rare relic (take 30 damage)",
        "[I am Awake] Upgrade all cards",
        "[I am Rich] Gain 999 gold",
    ]
    ui.display_event(
        "Mind Bloom",
        "A massive flower blooms before you, its petals shimmering.\n"
        "\"Tell me... what are you?\"",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        damage = 30
        player.lose_hp(damage)
        print(f"  You battle a phantom boss! Took {damage} damage. (HP: {player.hp}/{player.max_hp})")
        relic = get_random_relic(rarity=RelicRarity.RARE)
        if relic:
            player.add_relic(relic)
            print(f"  Victory! Gained rare relic: {relic.name}!")
        else:
            relic = get_random_relic()
            if relic:
                player.add_relic(relic)
                print(f"  Victory! Gained relic: {relic.name}!")
    elif choice == 1:
        upgraded = 0
        for card in player.deck:
            if not card.upgraded:
                card.upgrade()
                upgraded += 1
        print(f"  Enlightenment! Upgraded {upgraded} card(s)!")
    elif choice == 2:
        player.gold += 999
        print("  You are rich beyond measure! Gained 999 gold!")
        # Curse penalty
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  But greed has a cost... gained {curse.name}.")
    ui.press_enter()


def event_moai_head(player):
    """Moai Head: lose max HP, gain gold."""
    hp_loss = 7
    gold_gain = 100 + random.randint(0, 55)
    choices = [
        f"Offer blood (lose {hp_loss} Max HP, gain {gold_gain} gold)",
        "Leave",
    ]
    ui.display_event(
        "Moai Head",
        "A giant stone head sits at a crossroads, its mouth gaping wide.\n"
        "It demands a blood offering.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.max_hp -= hp_loss
        player.hp = min(player.hp, player.max_hp)
        player.gold += gold_gain
        print(f"  Lost {hp_loss} Max HP, gained {gold_gain} gold. (HP: {player.hp}/{player.max_hp})")
    else:
        print("  You walk past the stone head.")
    ui.press_enter()


def event_mysterious_sphere_act3(player):
    """Mysterious Sphere (Act 3): fight for a relic."""
    choices = [
        "Open the sphere (take 20-30 damage, gain a relic)",
        "Leave",
    ]
    ui.display_event(
        "Mysterious Sphere",
        "A pulsing sphere of energy floats before you.\n"
        "The power within is immense... and dangerous.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        damage = random.randint(20, 30)
        player.lose_hp(damage)
        print(f"  The sphere detonates! Took {damage} damage. (HP: {player.hp}/{player.max_hp})")
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  From the wreckage: {relic.name}!")
    else:
        print("  You leave the sphere alone.")
    ui.press_enter()


def event_secret_portal(player):
    """Secret Portal: enter Act 4 early (if keys collected)."""
    # Simplified: check for a flag or just offer the choice
    choices = [
        "Enter the portal (skip to the final act)",
        "Continue your journey",
    ]
    ui.display_event(
        "Secret Portal",
        "A shimmering portal tears open in the fabric of reality.\n"
        "You sense immense power beyond... and immense danger.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        # Check if the player has all keys (simplified check)
        has_keys = (
            player.has_relic("Emerald Key")
            or player.has_relic("Sapphire Key")
            or player.has_relic("Ruby Key")
            or True  # Simplified: always allow in this text version
        )
        if has_keys:
            print("  You step through the portal into the unknown...")
            player.act = 4  # Signal to game loop to skip to Act 4
        else:
            print("  The portal rejects you. You need all three keys.")
    else:
        print("  You turn away from the portal and continue onward.")
    ui.press_enter()


def event_sensory_stone(player):
    """Sensory Stone: gain 1-3 colorless cards."""
    num_cards = random.randint(1, 3)
    ui.display_event(
        "Sensory Stone",
        "You touch a smooth, warm stone embedded in the wall.\n"
        "Visions flash before your eyes, granting you new knowledge.",
        [f"Embrace the visions ({num_cards} colorless card(s))"],
    )
    ui.get_choice("What do you choose?", [f"Embrace the visions ({num_cards} colorless card(s))"])
    colorless_pool = get_cards_by_color(CardColor.COLORLESS)
    if colorless_pool:
        for _ in range(num_cards):
            selection = random.sample(colorless_pool, min(3, len(colorless_pool)))
            card_options = []
            cards = []
            for cid in selection:
                c = create_card(cid)
                cards.append(c)
                card_options.append(f"[{c.get_display_cost()}] {c.name} ({c.rarity.name})")
            card_choice = ui.get_choice("Choose a colorless card:", card_options,
                                        allow_cancel=True, cancel_text="Skip")
            if card_choice != -1:
                player.add_card_to_deck(cards[card_choice])
                print(f"  Gained: {cards[card_choice].name}!")
            else:
                print("  You skip this vision.")
    else:
        player.gold += 50
        print("  The visions reveal hidden gold! Gained 50 gold.")
    ui.press_enter()


def event_the_divine_fountain(player):
    """The Divine Fountain: remove all curses or leave."""
    curses = [c for c in player.deck if c.card_type == CardType.CURSE]
    if not curses:
        ui.display_event(
            "The Divine Fountain",
            "A fountain of crystal-clear water flows in a hidden chamber.\n"
            "You drink deeply, but feel no different. You carry no curses.",
            ["Leave"],
        )
        ui.get_choice("What do you choose?", ["Leave"])
        print("  You have no curses to purify.")
    else:
        choices = [
            f"Drink from the fountain (remove {len(curses)} curse(s))",
            "Leave",
        ]
        ui.display_event(
            "The Divine Fountain",
            "A fountain of crystal-clear water flows in a hidden chamber.\n"
            "Its holy water could cleanse even the darkest curse.",
            choices,
        )
        choice = ui.get_choice("What do you choose?", choices)
        if choice == 0:
            player.deck = [c for c in player.deck if c.card_type != CardType.CURSE]
            print(f"  Removed {len(curses)} curse(s) from your deck!")
        else:
            print("  You leave the fountain untouched.")
    ui.press_enter()


def event_tomb_of_lord_red_mask(player):
    """Tomb of Lord Red Mask: pay respects (lose gold) or desecrate (gain gold)."""
    gold_cost = min(player.gold, 50)
    gold_gain = random.randint(100, 180)
    choices = [
        f"Pay respects (lose {gold_cost} gold)",
        f"Desecrate the tomb (gain {gold_gain} gold)",
        "Leave",
    ]
    ui.display_event(
        "Tomb of Lord Red Mask",
        "You enter the tomb of the legendary Lord Red Mask.\n"
        "His golden death mask gleams in the dim torchlight.",
        choices,
    )
    choice = ui.get_choice("What do you choose?", choices)
    if choice == 0:
        player.gold -= gold_cost
        # Reward for paying respects
        healed = player.heal(max(1, int(player.max_hp * 0.15)))
        print(f"  You pay respects. Lost {gold_cost} gold, healed {healed} HP.")
    elif choice == 1:
        player.gold += gold_gain
        print(f"  You loot the tomb! Gained {gold_gain} gold!")
        # Possible curse
        if random.random() < 0.5:
            curse = _get_random_curse()
            player.add_card_to_deck(curse)
            print(f"  The tomb's curse follows you... gained {curse.name}.")
    else:
        print("  You leave the tomb in peace.")
    ui.press_enter()


def event_winding_halls_act3(player):
    """Winding Halls (Act 3): pick a direction with greater consequences."""
    choices = [
        "Go left (take 10 damage, gain a relic)",
        "Go right (gain 50 gold, gain a curse)",
        "Go straight (heal 15% HP)",
    ]
    ui.display_event(
        "Winding Halls",
        "The labyrinth splits into three treacherous passages.\n"
        "Each path radiates a different kind of energy.",
        choices,
    )
    choice = ui.get_choice("Which way?", choices)
    if choice == 0:
        damage = 10
        player.lose_hp(damage)
        print(f"  Took {damage} damage! (HP: {player.hp}/{player.max_hp})")
        relic = get_random_relic()
        if relic:
            player.add_relic(relic)
            print(f"  Found a relic: {relic.name}!")
    elif choice == 1:
        player.gold += 50
        curse = _get_random_curse()
        player.add_card_to_deck(curse)
        print(f"  Gained 50 gold, but also gained {curse.name}.")
    elif choice == 2:
        heal_amount = max(1, int(player.max_hp * 0.15))
        healed = player.heal(heal_amount)
        print(f"  A calm breeze. Healed {healed} HP!")
    ui.press_enter()


# =============================================================================
#  Event list
# =============================================================================

def get_act3_events():
    """Return list of all Act 3 event functions."""
    return [
        event_falling,
        event_mind_bloom,
        event_moai_head,
        event_mysterious_sphere_act3,
        event_secret_portal,
        event_sensory_stone,
        event_the_divine_fountain,
        event_tomb_of_lord_red_mask,
        event_winding_halls_act3,
    ]
