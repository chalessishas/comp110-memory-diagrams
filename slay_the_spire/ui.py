"""Text-based UI rendering for Slay the Spire."""
import os
import sys


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_separator(char="=", width=60):
    print(char * width)


def print_header(text, width=60):
    print_separator("=", width)
    padding = (width - len(text) - 2) // 2
    print(f"{'=' * padding} {text} {'=' * padding}")
    print_separator("=", width)


def print_subheader(text, width=60):
    print(f"--- {text} ---")


def get_input(prompt="> "):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n退出游戏。")
        sys.exit(0)


def get_choice(prompt, options, allow_cancel=False, cancel_text="取消"):
    """Display numbered options and get user choice.
    Returns 0-based index of chosen option, or -1 if cancelled."""
    print(prompt)
    for i, opt in enumerate(options):
        print(f"  {i + 1}. {opt}")
    if allow_cancel:
        print(f"  0. {cancel_text}")
    while True:
        choice = get_input()
        try:
            n = int(choice)
            if allow_cancel and n == 0:
                return -1
            if 1 <= n <= len(options):
                return n - 1
        except ValueError:
            pass
        print("无效选择，请重新输入。")


def get_yes_no(prompt):
    """Get yes/no input. Returns True for yes."""
    while True:
        print(f"{prompt} (y/n)")
        ans = get_input().lower()
        if ans in ("y", "yes", "是"):
            return True
        if ans in ("n", "no", "否"):
            return False


def display_combat(player, enemies, turn):
    """Display the full combat state."""
    print()
    print_separator("=")
    print(f"  回合 {turn}")
    print_separator("-")

    # Display enemies
    print("【敌人】")
    for i, e in enumerate(enemies):
        if e.is_alive:
            hp_bar = make_hp_bar(e.hp, e.max_hp, 20)
            intent_str = ""
            if e.intent:
                # Check for Runic Dome
                if player.has_relic("Runic Dome"):
                    intent_str = "Intent: ???"
                else:
                    if e.intent.damage > 0:
                        actual_dmg = e.get_attack_damage(e.intent.damage)
                        from slay_the_spire.enemy import Intent
                        display_intent = Intent(
                            e.intent.intent_type, damage=actual_dmg,
                            hits=e.intent.hits, block=e.intent.block
                        )
                        intent_str = f"Intent: {display_intent.display()}"
                    else:
                        intent_str = f"Intent: {e.intent.display()}"
            block_str = f" [BLK:{e.block}]" if e.block > 0 else ""
            effects_str = str(e.effects)
            eff_display = f" [{effects_str}]" if effects_str != "None" else ""
            print(f"  {i + 1}. {e.name} {hp_bar}{block_str}{eff_display}")
            if intent_str:
                print(f"     {intent_str}")
    print()

    # Display player
    print("【玩家】")
    hp_bar = make_hp_bar(player.hp, player.max_hp, 20)
    print(f"  HP: {hp_bar}  Energy: {'[E]' * player.energy}{'[ ]' * max(0, player.max_energy - player.energy)} ({player.energy}/{player.max_energy})")
    if player.block > 0:
        print(f"  Block: {player.block}")
    effects_str = str(player.effects)
    if effects_str != "None":
        print(f"  Effects: {effects_str}")
    if player.character_class == "defect" and player.orbs.orbs:
        print(f"  Orbs: {player.orbs}")
    from slay_the_spire.stance import StanceType
    if player.character_class == "watcher" and player.stance.current != StanceType.NONE:
        print(f"  Stance: {player.stance}")
    print()

    # Display hand
    print("【手牌】")
    if not player.hand:
        print("  (空)")
    else:
        for i, c in enumerate(player.hand):
            playable = "*" if c.can_play(player, None) else " "
            cost_str = c.get_display_cost()
            print(f"  {playable}{i + 1}. [{cost_str}] {c.name} - {c.description}")
    print()
    print(f"  牌堆: {len(player.draw_pile)} | 弃牌堆: {len(player.discard_pile)} | 消耗: {len(player.exhaust_pile)}")
    print_separator("-")


def display_combat_actions():
    """Display available combat actions."""
    print("操作: [数字]打出卡牌 | [p]使用药水 | [e]结束回合 | [d]查看牌组 | [m]查看地图 | [r]查看遗物")


def make_hp_bar(current, maximum, width=20):
    """Create a visual HP bar."""
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {current}/{maximum}"


def display_card_reward(cards):
    """Display card reward options."""
    print_subheader("卡牌奖励")
    for i, c in enumerate(cards):
        print(f"  {i + 1}. [{c.get_display_cost()}] {c.name} ({c.card_type.name} - {c.rarity.name})")
        print(f"     {c.description}")
    print(f"  0. 跳过")


def display_map(game_map, current_floor, act):
    """Display the map."""
    print_header(f"第 {act} 幕 - 地图")
    node_symbols = {
        "monster": "M",
        "elite": "E",
        "rest": "R",
        "shop": "$",
        "event": "?",
        "treasure": "T",
        "boss": "B",
    }
    # Display from top to bottom
    for row in range(len(game_map) - 1, -1, -1):
        row_nodes = game_map[row]
        line = f"  F{row + 1:2d} "
        for col in range(7):
            found = False
            for node in row_nodes:
                if node["col"] == col:
                    symbol = node_symbols.get(node["type"], "?")
                    if row + 1 == current_floor:
                        line += f"[{symbol}]"
                    elif row + 1 < current_floor:
                        line += f" {symbol.lower()} "
                    else:
                        line += f" {symbol} "
                    found = True
                    break
            if not found:
                line += "   "
        print(line)
    print()


def display_deck(deck):
    """Display the player's full deck."""
    print_subheader(f"牌组 ({len(deck)} 张)")
    attacks = [c for c in deck if c.card_type.name == "ATTACK"]
    skills = [c for c in deck if c.card_type.name == "SKILL"]
    powers = [c for c in deck if c.card_type.name == "POWER"]
    others = [c for c in deck if c.card_type.name not in ("ATTACK", "SKILL", "POWER")]

    for label, cards in [("攻击", attacks), ("技能", skills), ("能力", powers), ("其他", others)]:
        if cards:
            print(f"\n  [{label}]")
            for c in sorted(cards, key=lambda x: x.name):
                print(f"    [{c.get_display_cost()}] {c.name} - {c.description}")


def display_relics(relics):
    """Display the player's relics."""
    print_subheader(f"遗物 ({len(relics)})")
    for r in relics:
        counter_str = f" [{r.counter}]" if r.counter >= 0 else ""
        print(f"  - {r.name}{counter_str}: {r.description}")


def display_potions(potions):
    """Display the player's potions."""
    print_subheader("药水")
    for i, p in enumerate(potions):
        if p:
            print(f"  {i + 1}. {p.name} - {p.description}")
        else:
            print(f"  {i + 1}. [空]")


def display_shop(cards, relics, potions, card_remove_cost, player):
    """Display the shop."""
    print_header("商店")
    print(f"  金币: {player.gold}")
    print()

    print("  【卡牌】")
    for i, (card, price) in enumerate(cards):
        print(f"    {i + 1}. [{card.get_display_cost()}] {card.name} ({card.rarity.name}) - {price} 金")
    print()

    print("  【遗物】")
    for i, (relic, price) in enumerate(relics):
        print(f"    {len(cards) + i + 1}. {relic.name} - {price} 金")
    print()

    print("  【药水】")
    for i, (potion, price) in enumerate(potions):
        print(f"    {len(cards) + len(relics) + i + 1}. {potion.name} - {price} 金")
    print()

    print(f"  【移除卡牌】 - {card_remove_cost} 金")
    print(f"  0. 离开商店")


def display_rest_site(player, can_smith=True, can_rest=True, can_dig=False, can_lift=False, can_toke=False):
    """Display rest site options."""
    print_header("篝火")
    print(f"  HP: {player.hp}/{player.max_hp}")
    options = []
    if can_rest:
        heal_amount = int(player.max_hp * 0.3)
        options.append(f"休息 (回复 {heal_amount} HP)")
    if can_smith:
        options.append("升级一张卡牌")
    if can_dig:
        options.append("挖掘 (获得遗物)")
    if can_lift:
        options.append("锻炼 (获得力量)")
    if can_toke:
        options.append("净化 (移除一张卡)")
    return options


def display_event(title, description, choices):
    """Display an event."""
    print_header("事件")
    print(f"\n  {title}\n")
    for line in description.split("\n"):
        print(f"  {line}")
    print()
    for i, choice in enumerate(choices):
        print(f"  {i + 1}. {choice}")


def display_treasure(relic):
    """Display treasure chest contents."""
    print_header("宝箱")
    print(f"\n  获得遗物: {relic.name}")
    print(f"  {relic.description}")


def display_game_over(player, victory=False):
    """Display game over screen."""
    print()
    if victory:
        print_header("胜利!")
        print(f"\n  恭喜! {player.name} 成功通关!")
    else:
        print_header("失败")
        print(f"\n  {player.name} 倒下了...")
    print(f"  到达层数: {player.floor}")
    print(f"  金币: {player.gold}")
    print(f"  牌组大小: {len(player.deck)}")
    print(f"  遗物: {len(player.relics)}")
    print()


def display_boss_chest(relics):
    """Display boss chest with relic choices."""
    print_header("Boss 宝箱")
    print("\n  选择一个 Boss 遗物:")
    for i, r in enumerate(relics):
        print(f"  {i + 1}. {r.name} - {r.description}")


def press_enter():
    get_input("按回车继续...")
