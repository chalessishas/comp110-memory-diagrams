"""Main game loop for Slay the Spire text-based version."""
import random

from slay_the_spire import ui
from slay_the_spire.combat import Combat
from slay_the_spire.map_gen import generate_map, get_reachable_nodes
from slay_the_spire.shop import run_shop
from slay_the_spire.card import (
    create_card, get_cards_by_rarity,
    CardColor, CardRarity, CardType,
)
from slay_the_spire.relic import (
    get_random_relic, create_relic, RelicRarity,
)
from slay_the_spire.potion import get_random_potion
from slay_the_spire.enemy import Enemy, Intent, IntentType, random_hp


# =========================================================================
# Color mapping for characters
# =========================================================================
COLOR_MAP = {
    "ironclad": CardColor.RED,
    "silent": CardColor.GREEN,
    "defect": CardColor.BLUE,
    "watcher": CardColor.PURPLE,
}


# =========================================================================
# Enemy encounter pools  (lightweight inline enemies so the game is
# playable even when slay_the_spire/enemies/ is still empty)
# =========================================================================

class _SimpleEnemy(Enemy):
    """Generic enemy with a simple attack/defend pattern."""

    def __init__(self, name, hp, atk_lo, atk_hi, blk=0):
        super().__init__(name, hp)
        self._atk_lo = atk_lo
        self._atk_hi = atk_hi
        self._blk = blk

    def choose_intent(self, combat):
        roll = random.random()
        if roll < 0.65:
            dmg = random.randint(self._atk_lo, self._atk_hi)
            self.intent = Intent(IntentType.ATTACK, damage=dmg)
        elif roll < 0.85 and self._blk > 0:
            self.intent = Intent(IntentType.DEFEND, block=self._blk)
        else:
            self.intent = Intent(IntentType.ATTACK_DEBUFF,
                                 damage=random.randint(self._atk_lo - 1, self._atk_hi - 1))

    def take_turn(self, combat):
        if self.intent is None:
            return
        it = self.intent
        if it.damage > 0:
            actual = self.get_attack_damage(it.damage)
            for _ in range(it.hits):
                combat.deal_damage_to_player(actual, source=self)
        if it.block > 0:
            self.gain_block(it.block)
        if it.intent_type in (IntentType.DEBUFF, IntentType.ATTACK_DEBUFF):
            from slay_the_spire.effect import Weak, Vulnerable
            if random.random() < 0.5:
                combat.apply_effect_to_player("Weak", 1)
            else:
                combat.apply_effect_to_player("Vulnerable", 1)


def _make_monster(act):
    """Create a random normal monster group for the given act."""
    if act == 1:
        pool = [
            lambda: [_SimpleEnemy("Jaw Worm", random_hp(40, 44), 7, 11, 6)],
            lambda: [
                _SimpleEnemy("Louse", random_hp(10, 15), 5, 7),
                _SimpleEnemy("Louse", random_hp(10, 15), 5, 7),
            ],
            lambda: [_SimpleEnemy("Cultist", random_hp(48, 54), 6, 6)],
            lambda: [
                _SimpleEnemy("Slime (M)", random_hp(28, 32), 7, 10),
                _SimpleEnemy("Slime (S)", random_hp(12, 16), 4, 5),
            ],
            lambda: [
                _SimpleEnemy("Fungus Beast", random_hp(22, 28), 6, 6),
                _SimpleEnemy("Fungus Beast", random_hp(22, 28), 6, 6),
            ],
            lambda: [_SimpleEnemy("Blue Slaver", random_hp(46, 50), 8, 12)],
        ]
    elif act == 2:
        pool = [
            lambda: [
                _SimpleEnemy("Chosen", random_hp(95, 99), 10, 14, 8),
            ],
            lambda: [
                _SimpleEnemy("Byrd", random_hp(25, 31), 5, 6),
                _SimpleEnemy("Byrd", random_hp(25, 31), 5, 6),
                _SimpleEnemy("Byrd", random_hp(25, 31), 5, 6),
            ],
            lambda: [
                _SimpleEnemy("Spheric Guardian", random_hp(20, 24), 8, 10, 14),
                _SimpleEnemy("Shelled Parasite", random_hp(68, 72), 12, 18, 10),
            ],
            lambda: [
                _SimpleEnemy("Snake Plant", random_hp(75, 79), 10, 14, 8),
            ],
            lambda: [
                _SimpleEnemy("Centurion", random_hp(76, 80), 12, 16),
                _SimpleEnemy("Mystic", random_hp(48, 56), 6, 8),
            ],
        ]
    else:  # act 3
        pool = [
            lambda: [
                _SimpleEnemy("Darklings", random_hp(48, 56), 9, 13),
                _SimpleEnemy("Darklings", random_hp(48, 56), 9, 13),
                _SimpleEnemy("Darklings", random_hp(48, 56), 9, 13),
            ],
            lambda: [
                _SimpleEnemy("Reptomancer", random_hp(180, 190), 13, 16),
            ],
            lambda: [
                _SimpleEnemy("Writhing Mass", random_hp(160, 170), 15, 20, 12),
            ],
            lambda: [
                _SimpleEnemy("Jaw Worm Horde", random_hp(42, 46), 10, 14, 8),
                _SimpleEnemy("Jaw Worm Horde", random_hp(42, 46), 10, 14, 8),
                _SimpleEnemy("Jaw Worm Horde", random_hp(42, 46), 10, 14, 8),
            ],
        ]
    return random.choice(pool)()


def _make_elite(act):
    """Create a random elite encounter for the given act."""
    if act == 1:
        pool = [
            lambda: [_SimpleEnemy("Gremlin Nob", random_hp(82, 86), 14, 18, 0)],
            lambda: [_SimpleEnemy("Lagavulin", random_hp(109, 112), 10, 18, 8)],
            lambda: [_SimpleEnemy("Sentries", random_hp(38, 42), 8, 10, 6),
                      _SimpleEnemy("Sentries", random_hp(38, 42), 8, 10, 6),
                      _SimpleEnemy("Sentries", random_hp(38, 42), 8, 10, 6)],
        ]
    elif act == 2:
        pool = [
            lambda: [_SimpleEnemy("Book of Stabbing", random_hp(160, 168), 14, 20)],
            lambda: [
                _SimpleEnemy("Gremlin Leader", random_hp(140, 148), 12, 16),
                _SimpleEnemy("Gremlin", random_hp(20, 24), 6, 8),
                _SimpleEnemy("Gremlin", random_hp(20, 24), 6, 8),
            ],
            lambda: [
                _SimpleEnemy("Taskmaster", random_hp(54, 60), 10, 14),
                _SimpleEnemy("Taskmaster", random_hp(54, 60), 10, 14),
            ],
        ]
    else:
        pool = [
            lambda: [_SimpleEnemy("Giant Head", random_hp(500, 520), 13, 18, 12)],
            lambda: [_SimpleEnemy("Nemesis", random_hp(185, 200), 15, 25)],
            lambda: [_SimpleEnemy("Reptomancer", random_hp(180, 190), 13, 16)],
        ]
    return random.choice(pool)()


def _make_boss(act):
    """Create the boss encounter for the given act."""
    if act == 1:
        bosses = [
            lambda: [_SimpleEnemy("Slime Boss", random_hp(140, 150), 16, 24, 10)],
            lambda: [_SimpleEnemy("The Guardian", random_hp(240, 250), 14, 20, 14)],
            lambda: [_SimpleEnemy("Hexaghost", random_hp(250, 264), 12, 18)],
        ]
    elif act == 2:
        bosses = [
            lambda: [_SimpleEnemy("Automaton", random_hp(190, 200), 18, 24, 8)],
            lambda: [_SimpleEnemy("The Champ", random_hp(420, 440), 16, 22, 12)],
            lambda: [_SimpleEnemy("Collector", random_hp(282, 300), 14, 20)],
        ]
    else:
        bosses = [
            lambda: [_SimpleEnemy("Awakened One", random_hp(300, 320), 20, 28)],
            lambda: [_SimpleEnemy("Time Eater", random_hp(456, 480), 18, 26, 10)],
            lambda: [_SimpleEnemy("Donu & Deca", random_hp(250, 265), 16, 22, 16)],
        ]
    return random.choice(bosses)()


# =========================================================================
# Simple event system (inline since events/__init__.py is empty)
# =========================================================================

def _run_event(player, act):
    """Run a random event for the given act. Returns nothing."""
    events_pool = _get_events(act)
    event = random.choice(events_pool)
    event(player)


def _get_events(act):
    """Return a list of event callables for the given act."""
    return [
        _event_big_fish,
        _event_golden_shrine,
        _event_scrap_ooze,
        _event_living_wall,
        _event_the_cleric,
        _event_world_of_goop,
    ]


def _event_big_fish(player):
    choices = [
        "Heal to full HP.",
        f"Gain 5 Max HP. (current: {player.max_hp})",
        "Obtain a Relic. Gain a Curse.",
    ]
    ui.display_event("Big Fish", "A massive fish blocks the path.\nChoose wisely.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        healed = player.heal(player.max_hp)
        print(f"  Healed {healed} HP! ({player.hp}/{player.max_hp})")
    elif idx == 1:
        player.max_hp += 5
        player.hp += 5
        print(f"  Max HP is now {player.max_hp}!")
    else:
        relic = get_random_relic(RelicRarity.COMMON,
                                exclude={r.name for r in player.relics})
        if relic:
            player.add_relic(relic)
            print(f"  Obtained {relic.name}!")
        try:
            curse = create_card("regret")
        except Exception:
            curse = None
        if curse:
            player.add_card_to_deck(curse)
            print("  A Curse was added to your deck!")
    ui.press_enter()


def _event_golden_shrine(player):
    choices = [
        "Gain 100 Gold.",
        f"Gain 50 Gold and Gain 5 Max HP.",
        "Leave.",
    ]
    ui.display_event("Golden Shrine",
                     "A golden shrine hums with energy.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        player.gold += 100
        print(f"  Gained 100 Gold! ({player.gold})")
    elif idx == 1:
        player.gold += 50
        player.max_hp += 5
        player.hp += 5
        print(f"  Gained 50 Gold and 5 Max HP!")
    else:
        print("  You leave the shrine.")
    ui.press_enter()


def _event_scrap_ooze(player):
    choices = [
        "Reach inside. (lose 3-5 HP, gain a relic)",
        "Leave.",
    ]
    ui.display_event("Scrap Ooze",
                     "A pile of slime covers something valuable.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        loss = random.randint(3, 5)
        player.lose_hp(loss)
        print(f"  Lost {loss} HP! ({player.hp}/{player.max_hp})")
        relic = get_random_relic(RelicRarity.COMMON,
                                exclude={r.name for r in player.relics})
        if relic:
            player.add_relic(relic)
            print(f"  Obtained {relic.name}!")
    else:
        print("  You decide not to risk it.")
    ui.press_enter()


def _event_living_wall(player):
    choices = [
        "Forget. (remove a card from your deck)",
        "Change. (upgrade a card)",
        "Grow. (gain 7 Max HP)",
    ]
    ui.display_event("Living Wall",
                     "A wall of living vines speaks to you.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        _prompt_remove_card(player)
    elif idx == 1:
        _prompt_upgrade_card(player)
    else:
        player.max_hp += 7
        player.hp = min(player.hp + 7, player.max_hp)
        print(f"  Max HP is now {player.max_hp}!")
    ui.press_enter()


def _event_the_cleric(player):
    heal_cost = 35
    remove_cost = 50
    choices = [
        f"Heal (heal 25% HP) - {heal_cost} Gold",
        f"Purify (remove a card) - {remove_cost} Gold",
        "Leave.",
    ]
    ui.display_event("The Cleric",
                     "A cleric offers services for a fee.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        if player.gold >= heal_cost:
            player.gold -= heal_cost
            amount = int(player.max_hp * 0.25)
            player.heal(amount)
            print(f"  Healed {amount} HP! ({player.hp}/{player.max_hp})")
        else:
            print("  Not enough Gold!")
    elif idx == 1:
        if player.gold >= remove_cost:
            player.gold -= remove_cost
            _prompt_remove_card(player)
        else:
            print("  Not enough Gold!")
    else:
        print("  You leave the cleric.")
    ui.press_enter()


def _event_world_of_goop(player):
    choices = [
        "Gather Gold. (gain 75 Gold, lose 11 HP)",
        "Leave.",
    ]
    ui.display_event("World of Goop",
                     "Piles of gold sit in a pool of goop.", choices)
    idx = ui.get_choice("", choices)
    if idx == 0:
        player.gold += 75
        player.lose_hp(11)
        print(f"  Gained 75 Gold, lost 11 HP! ({player.hp}/{player.max_hp})")
    else:
        print("  You leave the goop behind.")
    ui.press_enter()


# =========================================================================
# Game class
# =========================================================================

class Game:
    """Orchestrates a full Slay-the-Spire run."""

    def __init__(self, player):
        self.player = player
        self.act = 1
        self.floor = 0
        self.map_data = None
        self.current_row = -1
        self.current_col = -1

    # ------------------------------------------------------------------
    # main entry point
    # ------------------------------------------------------------------
    def run(self):
        """Run the full game (acts 1-3, optional act 4)."""
        for act in range(1, 4):
            self.act = act
            self.player.act = act
            self.run_act(act)
            if self.player.hp <= 0:
                ui.display_game_over(self.player, victory=False)
                return

        # Victory
        ui.display_game_over(self.player, victory=True)

    # ------------------------------------------------------------------
    # per-act loop
    # ------------------------------------------------------------------
    def run_act(self, act):
        self.map_data = generate_map(act)
        self.current_row = -1
        self.current_col = -1
        self.floor = 0

        ui.clear_screen()
        ui.print_header(f"Act {act}")
        ui.press_enter()

        while True:
            # Determine reachable next nodes
            reachable = get_reachable_nodes(
                self.map_data, self.current_row, self.current_col)
            if not reachable:
                break  # no more nodes (past boss)

            # Display map and ask player to choose a path
            ui.clear_screen()
            ui.display_map(self.map_data, self.current_row + 1, act)
            self._display_player_status_bar()

            if len(reachable) == 1:
                node = reachable[0]
                print(f"  Next: Floor {node['row'] + 1} - {_node_label(node['type'])}")
                ui.press_enter()
            else:
                options = [
                    f"Floor {n['row'] + 1}, Col {n['col'] + 1} - "
                    f"{_node_label(n['type'])}"
                    for n in reachable
                ]
                idx = ui.get_choice("Choose your path:", options)
                node = reachable[idx]

            # Move player
            node["visited"] = True
            self.current_row = node["row"]
            self.current_col = node["col"]
            self.floor = node["row"] + 1
            self.player.floor = (act - 1) * 15 + self.floor

            # Relic: Maw Bank gold
            if self.player.has_relic("Maw Bank"):
                maw = self.player.get_relic("Maw Bank")
                if getattr(maw, 'active', True):
                    self.player.gold += 12

            # Execute the node
            self._execute_node(node)

            if self.player.hp <= 0:
                return

            # If we just fought the boss, break to next act
            if node["type"] == "boss":
                if self.player.hp > 0:
                    self._boss_reward()
                break

    # ------------------------------------------------------------------
    # node dispatch
    # ------------------------------------------------------------------
    def _execute_node(self, node):
        ntype = node["type"]
        if ntype == "monster":
            self._run_monster()
        elif ntype == "elite":
            self._run_elite()
        elif ntype == "boss":
            self._run_boss()
        elif ntype == "rest":
            self._run_rest_site()
        elif ntype == "shop":
            self._run_shop()
        elif ntype == "event":
            self._run_event()
        elif ntype == "treasure":
            self._run_treasure()

    # ------------------------------------------------------------------
    # combat nodes
    # ------------------------------------------------------------------
    def _run_monster(self):
        enemies = _make_monster(self.act)
        self._run_combat(enemies, is_elite=False, is_boss=False)

    def _run_elite(self):
        enemies = _make_elite(self.act)
        self._run_combat(enemies, is_elite=True, is_boss=False)

    def _run_boss(self):
        enemies = _make_boss(self.act)
        self._run_combat(enemies, is_elite=False, is_boss=True)

    def _run_combat(self, enemies, is_elite, is_boss):
        ui.clear_screen()
        names = ", ".join(e.name for e in enemies)
        label = "BOSS" if is_boss else ("ELITE" if is_elite else "Combat")
        ui.print_header(f"{label}: {names}")
        ui.press_enter()

        combat = Combat(self.player, enemies, is_boss=is_boss, is_elite=is_elite)
        victory = combat.run()

        if not victory:
            return  # player died

        # --- rewards ---
        # Gold
        gold = self._calc_gold_reward(enemies, is_elite, is_boss)
        self.player.gold += gold
        self.player.gold_gained_this_combat = gold
        print(f"\n  Gold gained: {gold}  (Total: {self.player.gold})")

        # Potion chance
        self._maybe_gain_potion(is_elite)

        # Card reward
        if is_boss:
            # Bosses give card reward too
            self._card_reward(is_elite=False)
        elif is_elite:
            # Elites give a relic + card
            relic = self._get_elite_relic()
            if relic:
                self.player.add_relic(relic)
                print(f"  Obtained relic: {relic.name} - {relic.description}")
            self._card_reward(is_elite=True)
        else:
            self._card_reward(is_elite=False)

        # Burning Blood relic (heals at end of combat) already handled via
        # relic.on_combat_end in Combat.cleanup

        ui.press_enter()

    def _calc_gold_reward(self, enemies, is_elite, is_boss):
        base = 0
        if is_boss:
            base = random.randint(95, 105)
        elif is_elite:
            base = random.randint(25, 35)
        else:
            base = random.randint(10, 20)
        # Relic: Gold bonus
        if self.player.has_relic("Golden Idol"):
            base = int(base * 1.25)
        return base

    def _get_elite_relic(self):
        """Get a relic reward for elite fight."""
        owned = {r.name for r in self.player.relics}
        if self.player.has_relic("Black Star"):
            # Two relic choices (simplified: just give one better rarity)
            relic = get_random_relic(RelicRarity.RARE, exclude=owned)
            if relic:
                return relic
        # Normal: common/uncommon/rare weighted
        roll = random.random()
        if roll < 0.50:
            rarity = RelicRarity.COMMON
        elif roll < 0.83:
            rarity = RelicRarity.UNCOMMON
        else:
            rarity = RelicRarity.RARE
        return get_random_relic(rarity, exclude=owned,
                               color=self.player.character_class)

    # ------------------------------------------------------------------
    # card reward
    # ------------------------------------------------------------------
    def _card_reward(self, is_elite=False):
        color = COLOR_MAP.get(self.player.character_class, CardColor.COLORLESS)
        num_cards = 3
        if self.player.has_relic("Question Card"):
            num_cards += 1
        if self.player.has_relic("Busted Crown"):
            num_cards -= 2
        if self.player.has_relic("Prayer Wheel") and not is_elite:
            # Two card rewards
            self._show_card_reward(color, max(1, num_cards))
            self._show_card_reward(color, max(1, num_cards))
            return
        self._show_card_reward(color, max(1, num_cards))

    def _show_card_reward(self, color, num_cards):
        cards = []
        for _ in range(num_cards):
            rarity = self._roll_card_rarity()
            pool = get_cards_by_rarity(color, rarity)
            if not pool:
                pool = get_cards_by_rarity(color, CardRarity.COMMON)
            if pool:
                card = create_card(random.choice(pool))
                cards.append(card)
        if not cards:
            return

        # Relic: Singing Bowl option
        singing_bowl = self.player.has_relic("Singing Bowl")

        ui.display_card_reward(cards)
        if singing_bowl:
            print(f"  {len(cards) + 1}. Gain 2 Max HP (Singing Bowl)")

        while True:
            choice = ui.get_input()
            try:
                n = int(choice)
                if n == 0:
                    print("  Skipped card reward.")
                    return
                if singing_bowl and n == len(cards) + 1:
                    self.player.max_hp += 2
                    self.player.hp += 2
                    print(f"  Gained 2 Max HP! ({self.player.hp}/{self.player.max_hp})")
                    return
                if 1 <= n <= len(cards):
                    chosen = cards[n - 1].copy()
                    # Egg relics auto-upgrade
                    if (chosen.card_type == CardType.ATTACK
                            and self.player.has_relic("Molten Egg")):
                        chosen.upgrade()
                    elif (chosen.card_type == CardType.SKILL
                          and self.player.has_relic("Toxic Egg")):
                        chosen.upgrade()
                    elif (chosen.card_type == CardType.POWER
                          and self.player.has_relic("Frozen Egg")):
                        chosen.upgrade()
                    self.player.add_card_to_deck(chosen)
                    print(f"  Added {chosen.name} to your deck!")
                    return
            except ValueError:
                pass
            print("  Invalid choice.")

    def _roll_card_rarity(self):
        roll = random.random()
        if roll < 0.55:
            return CardRarity.COMMON
        elif roll < 0.88:
            return CardRarity.UNCOMMON
        else:
            return CardRarity.RARE

    # ------------------------------------------------------------------
    # potion chance
    # ------------------------------------------------------------------
    def _maybe_gain_potion(self, is_elite):
        if self.player.has_relic("Sozu"):
            return
        chance = 0.4 if is_elite else 0.2
        if self.player.has_relic("White Beast Statue"):
            chance = 1.0
        if random.random() < chance:
            potion = get_random_potion(self.player.character_class)
            if self.player.add_potion(potion):
                print(f"  Found a potion: {potion.name}!")
            else:
                print(f"  Found a potion ({potion.name}) but your slots are full!")

    # ------------------------------------------------------------------
    # rest site
    # ------------------------------------------------------------------
    def _run_rest_site(self):
        ui.clear_screen()

        can_smith = not self.player.has_relic("Fusion Hammer")
        can_rest = not self.player.has_relic("Coffee Dripper")

        # Girya
        can_lift = (self.player.has_relic("Girya")
                    and self.player.get_relic("Girya").counter < 3)
        can_toke = self.player.has_relic("Peace Pipe")
        can_dig = self.player.has_relic("Shovel")

        options = ui.display_rest_site(
            self.player,
            can_smith=can_smith, can_rest=can_rest,
            can_dig=can_dig, can_lift=can_lift, can_toke=can_toke,
        )
        if not options:
            print("  No options available at this rest site!")
            ui.press_enter()
            return

        idx = ui.get_choice("Choose an action:", options)
        action_text = options[idx]

        if "Rest" in action_text or "休息" in action_text:
            heal_amount = int(self.player.max_hp * 0.3)
            # Regal Pillow: +15 HP
            if self.player.has_relic("Regal Pillow"):
                heal_amount += 15
            actual = self.player.heal(heal_amount)
            print(f"  Rested and healed {actual} HP! ({self.player.hp}/{self.player.max_hp})")
            # Dream Catcher: card reward on rest
            if self.player.has_relic("Dream Catcher"):
                color = COLOR_MAP.get(self.player.character_class, CardColor.COLORLESS)
                self._show_card_reward(color, 3)
            # Relic: on_rest
            for relic in self.player.relics:
                relic.on_rest(self.player)

        elif "Smith" in action_text or "upgrade" in action_text.lower() or "升级" in action_text:
            _prompt_upgrade_card(self.player)

        elif "Lift" in action_text or "锻炼" in action_text:
            from slay_the_spire.effect import Strength
            girya = self.player.get_relic("Girya")
            girya.counter += 1
            print(f"  Lifted! Girya counter: {girya.counter}/3")
            print("  (You will gain 1 Strength at the start of each combat from Girya.)")

        elif "Toke" in action_text or "净化" in action_text:
            _prompt_remove_card(self.player)

        elif "Dig" in action_text or "挖掘" in action_text:
            owned = {r.name for r in self.player.relics}
            relic = get_random_relic(exclude=owned,
                                    color=self.player.character_class)
            if relic:
                self.player.add_relic(relic)
                print(f"  Dug up a relic: {relic.name}!")
                print(f"  {relic.description}")

        ui.press_enter()

    # ------------------------------------------------------------------
    # shop
    # ------------------------------------------------------------------
    def _run_shop(self):
        # Meal Ticket: heal 15 on shop entry
        if self.player.has_relic("Meal Ticket"):
            self.player.heal(15)
            print(f"  Meal Ticket: healed 15 HP! ({self.player.hp}/{self.player.max_hp})")
        run_shop(self.player)

    # ------------------------------------------------------------------
    # event
    # ------------------------------------------------------------------
    def _run_event(self):
        # Juzu Bracelet: skip normal encounters from events
        ui.clear_screen()
        _run_event(self.player, self.act)

    # ------------------------------------------------------------------
    # treasure
    # ------------------------------------------------------------------
    def _run_treasure(self):
        ui.clear_screen()
        owned = {r.name for r in self.player.relics}
        # Roll rarity for small chest
        roll = random.random()
        if roll < 0.50:
            rarity = RelicRarity.COMMON
        elif roll < 0.83:
            rarity = RelicRarity.UNCOMMON
        else:
            rarity = RelicRarity.RARE
        relic = get_random_relic(rarity, exclude=owned,
                                color=self.player.character_class)
        if relic:
            self.player.add_relic(relic)
            ui.display_treasure(relic)
            # Cursed Key: gain a curse on chest open
            if self.player.has_relic("Cursed Key"):
                try:
                    curse = create_card("regret")
                    self.player.add_card_to_deck(curse)
                    print("  Cursed Key: a curse was added to your deck!")
                except Exception:
                    pass
            # Matryoshka: extra relic from chests
            if self.player.has_relic("Matryoshka"):
                mat = self.player.get_relic("Matryoshka")
                if mat.counter > 0:
                    mat.counter -= 1
                    extra = get_random_relic(RelicRarity.COMMON,
                                            exclude={r.name for r in self.player.relics})
                    if extra:
                        self.player.add_relic(extra)
                        print(f"  Matryoshka: also obtained {extra.name}!")
        else:
            print("  The chest is empty...")
        ui.press_enter()

    # ------------------------------------------------------------------
    # boss reward (3 boss relics, pick 1)
    # ------------------------------------------------------------------
    def _boss_reward(self):
        ui.clear_screen()
        owned = {r.name for r in self.player.relics}
        boss_relics = []
        attempts = 0
        while len(boss_relics) < 3 and attempts < 30:
            r = get_random_relic(RelicRarity.BOSS, exclude=owned)
            if r and r.name not in {br.name for br in boss_relics}:
                boss_relics.append(r)
                owned.add(r.name)
            attempts += 1

        if not boss_relics:
            print("  No boss relics available.")
            ui.press_enter()
            return

        ui.display_boss_chest(boss_relics)
        options = [f"{r.name} - {r.description}" for r in boss_relics]
        options.append("Skip")
        idx = ui.get_choice("", options)
        if idx < len(boss_relics):
            chosen = boss_relics[idx]
            self.player.add_relic(chosen)
            print(f"\n  Obtained boss relic: {chosen.name}!")
        else:
            print("  Skipped boss relic.")
        ui.press_enter()

    # ------------------------------------------------------------------
    # UI helper
    # ------------------------------------------------------------------
    def _display_player_status_bar(self):
        p = self.player
        print(f"  [{p.name}] HP: {p.hp}/{p.max_hp} | Gold: {p.gold} "
              f"| Deck: {len(p.deck)} | Floor: {self.floor} "
              f"| Act: {self.act}")
        print(f"  Relics: {p.relics_str()}")
        print(f"  Potions: {p.potions_str()}")
        print()


# =========================================================================
# Helpers
# =========================================================================

def _node_label(node_type):
    """Human-readable label for a node type."""
    labels = {
        "monster": "Monster",
        "elite": "Elite (hard)",
        "rest": "Rest Site",
        "shop": "Shop",
        "event": "? Event",
        "treasure": "Treasure",
        "boss": "BOSS",
    }
    return labels.get(node_type, node_type)


def _prompt_upgrade_card(player):
    """Let the player choose a card to upgrade."""
    upgradable = [(i, c) for i, c in enumerate(player.deck) if not c.upgraded]
    if not upgradable:
        print("  No upgradable cards in your deck!")
        return
    print("\nChoose a card to upgrade:")
    for j, (i, c) in enumerate(upgradable):
        print(f"  {j + 1}. {c.short_desc()}")
    print(f"  0. Cancel")
    choice = ui.get_input()
    try:
        n = int(choice)
        if n == 0:
            return
        if 1 <= n <= len(upgradable):
            idx, card = upgradable[n - 1]
            card.upgrade()
            print(f"  Upgraded {card.name}!")
    except ValueError:
        pass


def _prompt_remove_card(player):
    """Let the player choose a card to remove from deck."""
    if not player.deck:
        print("  No cards to remove!")
        return
    print("\nChoose a card to remove:")
    for i, c in enumerate(player.deck):
        print(f"  {i + 1}. {c.short_desc()}")
    print(f"  0. Cancel")
    choice = ui.get_input()
    try:
        n = int(choice) - 1
        if n == -1:
            return
        if 0 <= n < len(player.deck):
            removed = player.deck.pop(n)
            print(f"  Removed {removed.name} from your deck!")
    except ValueError:
        pass
