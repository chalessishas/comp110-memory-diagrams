"""Shop system for Slay the Spire."""
import random
from slay_the_spire import ui
from slay_the_spire.card import (create_card, get_cards_by_rarity, CardColor,
                                  CardRarity, CardType)
from slay_the_spire.relic import get_random_relic, RelicRarity
from slay_the_spire.potion import get_random_potion


COLOR_MAP = {
    "ironclad": CardColor.RED,
    "silent": CardColor.GREEN,
    "defect": CardColor.BLUE,
    "watcher": CardColor.PURPLE,
}

CARD_PRICES = {
    CardRarity.COMMON: (45, 55),
    CardRarity.UNCOMMON: (68, 82),
    CardRarity.RARE: (135, 165),
}

RELIC_PRICES = {
    RelicRarity.COMMON: (143, 157),
    RelicRarity.UNCOMMON: (238, 262),
    RelicRarity.RARE: (285, 315),
    RelicRarity.SHOP: (143, 157),
}


def generate_shop_items(player):
    """Generate shop inventory."""
    color = COLOR_MAP.get(player.character_class, CardColor.COLORLESS)

    # Cards: 2 attack, 2 skill, 1 power (mixed rarities), 2 colorless
    cards = []

    # Colored cards
    for card_type_filter, count in [("attack", 2), ("skill", 2), ("power", 1)]:
        for _ in range(count):
            rarity = _roll_rarity()
            card_ids = get_cards_by_rarity(color, rarity)
            if not card_ids:
                card_ids = get_cards_by_rarity(color, CardRarity.COMMON)
            if card_ids:
                card = create_card(random.choice(card_ids))
                if card_type_filter == "attack" and card.card_type != CardType.ATTACK:
                    # try again
                    card_ids2 = [cid for cid in card_ids]
                    random.shuffle(card_ids2)
                    for cid in card_ids2:
                        c = create_card(cid)
                        if c.card_type == CardType.ATTACK:
                            card = c
                            break
                price_range = CARD_PRICES.get(card.rarity, (50, 60))
                price = random.randint(*price_range)
                cards.append((card, price))

    # Colorless cards
    for _ in range(2):
        rarity = CardRarity.UNCOMMON if random.random() < 0.7 else CardRarity.RARE
        colorless_ids = get_cards_by_rarity(CardColor.COLORLESS, rarity)
        if colorless_ids:
            card = create_card(random.choice(colorless_ids))
            price = random.randint(81, 99) if rarity == CardRarity.UNCOMMON else random.randint(162, 198)
            cards.append((card, price))

    # Relics: 3 relics
    owned_relics = {r.name for r in player.relics}
    relics = []
    for rarity in [RelicRarity.COMMON, RelicRarity.UNCOMMON, RelicRarity.SHOP]:
        relic = get_random_relic(rarity, exclude=owned_relics, color=player.character_class)
        if relic is None:
            relic = get_random_relic(rarity, exclude=owned_relics)
        if relic:
            price_range = RELIC_PRICES.get(rarity, (150, 170))
            price = random.randint(*price_range)
            relics.append((relic, price))
            owned_relics.add(relic.name)

    # Potions: 3 potions
    potions = []
    for _ in range(3):
        potion = get_random_potion(player.character_class)
        price = random.randint(48, 52)
        potions.append((potion, price))

    # Card removal cost
    base_remove_cost = 75
    if player.has_relic("Smiling Mask"):
        remove_cost = 50
    else:
        # Increases by 25 for each removal
        remove_cost = base_remove_cost

    # Membership Card: 50% off
    if player.has_relic("Membership Card"):
        cards = [(c, p // 2) for c, p in cards]
        relics = [(r, p // 2) for r, p in relics]
        potions = [(pot, p // 2) for pot, p in potions]
        remove_cost = remove_cost // 2

    # The Courier: 20% off
    if player.has_relic("The Courier"):
        cards = [(c, int(p * 0.8)) for c, p in cards]
        relics = [(r, int(p * 0.8)) for r, p in relics]
        potions = [(pot, int(p * 0.8)) for pot, p in potions]

    return cards, relics, potions, remove_cost


def run_shop(player):
    """Run the shop interaction."""
    # Relic: on_enter_shop
    for relic in player.relics:
        relic.on_enter_shop(player)

    cards, relics, potions, remove_cost = generate_shop_items(player)
    bought_indices = set()

    while True:
        ui.clear_screen()
        ui.display_shop(cards, relics, potions, remove_cost, player)

        choice = ui.get_input("选择购买项目编号 (0=离开): ")
        try:
            idx = int(choice)
        except ValueError:
            if choice.lower() == 'r':
                # Card removal
                idx = -2
            else:
                continue

        if idx == 0:
            break

        if idx == -2 or choice.lower() == 'r':
            # Card removal
            if player.gold >= remove_cost:
                _handle_card_removal(player, remove_cost)
            else:
                print("  金币不足!")
                ui.press_enter()
            continue

        total_items = len(cards) + len(relics) + len(potions)
        if idx < 1 or idx > total_items:
            continue

        if idx in bought_indices:
            print("  已售罄!")
            ui.press_enter()
            continue

        if idx <= len(cards):
            # Buy card
            card, price = cards[idx - 1]
            if player.gold >= price:
                player.gold -= price
                new_card = card.copy()
                # Egg relics
                if new_card.card_type == CardType.ATTACK and player.has_relic("Molten Egg"):
                    new_card.upgrade()
                elif new_card.card_type == CardType.SKILL and player.has_relic("Toxic Egg"):
                    new_card.upgrade()
                elif new_card.card_type == CardType.POWER and player.has_relic("Frozen Egg"):
                    new_card.upgrade()
                player.add_card_to_deck(new_card)
                bought_indices.add(idx)
                print(f"  购买了 {card.name}!")
                # Ceramic Fish
                if player.has_relic("Ceramic Fish"):
                    player.gold += 9
            else:
                print("  金币不足!")
            ui.press_enter()

        elif idx <= len(cards) + len(relics):
            # Buy relic
            r_idx = idx - len(cards) - 1
            relic, price = relics[r_idx]
            if player.gold >= price:
                player.gold -= price
                player.add_relic(relic)
                bought_indices.add(idx)
                print(f"  购买了 {relic.name}!")
            else:
                print("  金币不足!")
            ui.press_enter()

        else:
            # Buy potion
            p_idx = idx - len(cards) - len(relics) - 1
            potion, price = potions[p_idx]
            if player.has_relic("Sozu"):
                print("  Sozu: 无法获得药水!")
                ui.press_enter()
                continue
            if player.gold >= price:
                if player.add_potion(potion):
                    player.gold -= price
                    bought_indices.add(idx)
                    print(f"  购买了 {potion.name}!")
                else:
                    print("  药水栏已满!")
            else:
                print("  金币不足!")
            ui.press_enter()

    # Maw Bank: spent gold at shop
    if player.has_relic("Maw Bank"):
        maw = player.get_relic("Maw Bank")
        if any(i in bought_indices for i in range(1, len(cards) + len(relics) + len(potions) + 1)):
            maw.active = False


def _roll_rarity():
    roll = random.random()
    if roll < 0.55:
        return CardRarity.COMMON
    elif roll < 0.88:
        return CardRarity.UNCOMMON
    else:
        return CardRarity.RARE


def _handle_card_removal(player, cost):
    """Handle card removal at shop."""
    if player.gold < cost:
        print("  金币不足!")
        return
    print("\n选择要移除的卡牌:")
    for i, c in enumerate(player.deck):
        print(f"  {i + 1}. {c.short_desc()}")
    print(f"  0. 取消")
    choice = ui.get_input()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(player.deck):
            removed = player.deck.pop(idx)
            player.gold -= cost
            print(f"  移除了 {removed.name}!")
        elif idx == -1:
            return
    except ValueError:
        pass
    ui.press_enter()
