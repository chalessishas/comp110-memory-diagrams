"""Combat engine for Slay the Spire."""
import random
from slay_the_spire.card import CardType, CardTarget
from slay_the_spire.orb import OrbType
from slay_the_spire.stance import StanceType
from slay_the_spire import ui


class Combat:
    """Manages a single combat encounter."""

    def __init__(self, player, enemies, is_boss=False, is_elite=False):
        self.player = player
        self.enemies = enemies
        self.is_boss = is_boss
        self.is_elite = is_elite
        self.turn = 0
        self.escaped = False
        self.victory = False
        self.game_over = False

    def run(self):
        """Run the full combat loop. Returns True if player won."""
        self.setup()
        while not self.is_finished():
            self.turn += 1
            self.player_turn()
            if self.is_finished():
                break
            self.enemy_turn()
            if self.is_finished():
                break
        self.cleanup()
        return self.victory

    def setup(self):
        """Initialize combat."""
        self.player.start_combat()

        # Relic: on_combat_start
        for relic in self.player.relics:
            relic.on_combat_start(self.player, self)

        # Enemy setup
        for enemy in self.enemies:
            enemy.choose_intent(self)

        # Innate cards: move to top of draw pile
        innate_cards = [c for c in self.player.draw_pile if c.innate]
        for c in innate_cards:
            self.player.draw_pile.remove(c)
            self.player.draw_pile.append(c)  # append = top of pile (drawn first)

    def player_turn(self):
        """Handle the player's turn."""
        self.player.start_turn()

        # Relic: on_turn_start
        for relic in self.player.relics:
            relic.on_turn_start(self.player, self)

        # Noxious Fumes
        if self.player.effects.has("Noxious Fumes"):
            from slay_the_spire.effect import Poison
            stacks = self.player.effects.get_stacks("Noxious Fumes")
            for e in self.enemies:
                if e.is_alive:
                    e.effects.add(Poison(stacks))

        # Infinite Blades
        if self.player.effects.has("Infinite Blades"):
            from slay_the_spire.card import create_card
            try:
                shiv = create_card("shiv")
                if len(self.player.hand) < 10:
                    self.player.hand.append(shiv)
            except:
                pass

        # Creative AI
        if self.player.effects.has("Creative AI"):
            # Add random power to hand - simplified
            pass

        # Battle Hymn
        if self.player.effects.has("Battle Hymn"):
            from slay_the_spire.card import create_card
            stacks = self.player.effects.get_stacks("Battle Hymn")
            for _ in range(stacks):
                try:
                    smite = create_card("smite")
                    if len(self.player.hand) < 10:
                        self.player.hand.append(smite)
                except:
                    pass

        # Demon Form
        if self.player.effects.has("Demon Form"):
            from slay_the_spire.effect import Strength
            self.player.effects.add(Strength(self.player.effects.get_stacks("Demon Form")))

        # Devotion (Mantra)
        if self.player.effects.has("Devotion"):
            from slay_the_spire.effect import Mantra
            self.player.effects.add(Mantra(self.player.effects.get_stacks("Devotion")))
            if self.player.effects.get_stacks("Mantra") >= 10:
                self.player.effects.reduce("Mantra", 10)
                self.player.stance.enter(StanceType.DIVINITY)
                self.player.gain_energy(3)

        # Snecko Eye: randomize hand costs
        if self.player.has_relic("Snecko Eye"):
            for c in self.player.hand:
                if c.cost >= 0:
                    c.cost_for_turn = random.randint(0, 3)

        # Combat UI loop
        while True:
            if self.is_finished():
                break

            ui.display_combat(self.player, self.enemies, self.turn)
            ui.display_combat_actions()

            action = ui.get_input()

            if action.lower() == 'e':
                break  # end turn
            elif action.lower() == 'p':
                self.handle_potion_use()
            elif action.lower() == 'd':
                ui.display_deck(self.player.deck)
                ui.press_enter()
            elif action.lower() == 'r':
                ui.display_relics(self.player.relics)
                ui.press_enter()
            elif action.lower() == 'm':
                print(f"  牌堆 ({len(self.player.draw_pile)}): 按 's' 查看" if self.player.has_relic("Frozen Eye") else f"  牌堆: {len(self.player.draw_pile)} 张")
                print(f"  弃牌堆 ({len(self.player.discard_pile)}):")
                for c in self.player.discard_pile:
                    print(f"    {c.short_desc()}")
                print(f"  消耗堆 ({len(self.player.exhaust_pile)}):")
                for c in self.player.exhaust_pile:
                    print(f"    {c.short_desc()}")
                ui.press_enter()
            else:
                try:
                    card_idx = int(action) - 1
                    if 0 <= card_idx < len(self.player.hand):
                        self.play_card(card_idx)
                    else:
                        print("无效的卡牌编号。")
                except ValueError:
                    print("无效输入。输入卡牌编号打出，'e' 结束回合，'p' 使用药水。")

        # End of player turn
        self.player.end_turn()

        # Orb passives (Defect)
        if self.player.character_class == "defect":
            focus = self.player.effects.get_stacks("Focus")
            loop_extra = self.player.effects.get_stacks("Loop") if self.player.effects.has("Loop") else 0
            for idx, orb in enumerate(self.player.orbs.orbs):
                times = 1 + (loop_extra if idx == 0 else 0)
                for _ in range(times):
                    if orb.orb_type == OrbType.LIGHTNING:
                        dmg = 3 + max(0, focus)
                        target = random.choice([e for e in self.enemies if e.is_alive]) if any(e.is_alive for e in self.enemies) else None
                        if target:
                            self.deal_damage_to_enemy(target, dmg)
                            print(f"  Lightning orb 对 {target.name} 造成 {dmg} 伤害")
                    elif orb.orb_type == OrbType.FROST:
                        blk = 2 + max(0, focus)
                        self.player.gain_block_raw(blk)
                        print(f"  Frost orb 给予 {blk} 格挡")
                    elif orb.orb_type == OrbType.DARK:
                        orb.dark_damage += 6 + max(0, focus)
                    elif orb.orb_type == OrbType.PLASMA:
                        self.player.gain_energy(1)

        # Relic: on_turn_end
        for relic in self.player.relics:
            relic.on_turn_end(self.player, self)

        # Combust: damage all enemies
        if self.player.effects.has("Combust"):
            stacks = self.player.effects.get_stacks("Combust")
            for e in self.enemies:
                if e.is_alive:
                    e.take_damage(stacks, self)

        # A Thousand Cuts is per-card, handled in play_card

        # Like Water: if in Calm, gain block
        if self.player.effects.has("Like Water"):
            if self.player.stance.is_in(StanceType.CALM):
                self.player.gain_block_raw(self.player.effects.get_stacks("Like Water"))

    def enemy_turn(self):
        """Handle all enemies' turns."""
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            enemy.start_turn()
            if not enemy.is_alive:  # died to poison
                print(f"  {enemy.name} 因中毒而死亡!")
                self.on_enemy_death(enemy)
                continue

            enemy.take_turn(self)

            if self.player.hp <= 0:
                self.game_over = True
                return

            enemy.end_turn()
            enemy.choose_intent(self)

        # Beat of Death
        # (handled per card play)

    def play_card(self, hand_idx):
        """Play a card from hand."""
        if hand_idx < 0 or hand_idx >= len(self.player.hand):
            return False

        card = self.player.hand[hand_idx]

        # Check Velvet Choker
        if self.player.has_relic("Velvet Choker"):
            choker = self.player.get_relic("Velvet Choker")
            if choker.counter >= 6:
                print("  Velvet Choker: 本回合已打出6张牌!")
                return False

        # Check Entangled
        if self.player.effects.has("Entangled") and card.card_type == CardType.ATTACK:
            print("  被缠绕了，无法打出攻击牌!")
            return False

        if not card.can_play(self.player, self):
            print("  无法打出此牌! (能量不足或不可打出)")
            return False

        # Determine target
        target = None
        if card.target == CardTarget.ENEMY:
            alive = [e for e in self.enemies if e.is_alive]
            if len(alive) == 0:
                return False
            elif len(alive) == 1:
                target = alive[0]
            else:
                print("选择目标:")
                for i, e in enumerate(alive):
                    print(f"  {i + 1}. {e.name} (HP: {e.hp}/{e.max_hp})")
                choice = ui.get_input()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(alive):
                        target = alive[idx]
                    else:
                        return False
                except ValueError:
                    return False

        # Spend energy
        effective_cost = card.get_effective_cost(self.player)
        x_amount = 0
        if card.cost == -1:  # X cost
            x_amount = self.player.energy
            if self.player.has_relic("Chemical X"):
                x_amount += 2
            self.player.spend_energy(self.player.energy)
        elif effective_cost > 0:
            self.player.spend_energy(effective_cost)

        # Remove from hand
        self.player.hand.pop(hand_idx)

        print(f"  打出 {card.name}!")

        # Track play counts
        self.player.cards_played_this_turn += 1
        self.player.cards_played_this_combat += 1
        if card.card_type == CardType.ATTACK:
            self.player.attacks_played_this_turn += 1
        elif card.card_type == CardType.SKILL:
            self.player.skills_played_this_turn += 1
        elif card.card_type == CardType.POWER:
            self.player.powers_played_this_turn += 1

        # Execute card effect
        self.execute_card(card, target, x_amount)

        # After Image: gain 1 block per card played
        if self.player.effects.has("After Image"):
            self.player.gain_block_raw(self.player.effects.get_stacks("After Image"))

        # A Thousand Cuts
        if self.player.effects.has("A Thousand Cuts"):
            dmg = self.player.effects.get_stacks("A Thousand Cuts")
            for e in self.enemies:
                if e.is_alive:
                    self.deal_damage_to_enemy(e, dmg)

        # Rage: gain block on attack play
        if self.player.effects.has("Rage") and card.card_type == CardType.ATTACK:
            self.player.gain_block_raw(self.player.effects.get_stacks("Rage"))

        # Beat of Death (enemy effect)
        for e in self.enemies:
            if e.is_alive and e.effects.has("Beat of Death"):
                self.player.lose_hp(e.effects.get_stacks("Beat of Death"))

        # Relic: on_card_play
        for relic in self.player.relics:
            relic.on_card_play(self.player, card, self)

        # Enrage (enemy: gain str when skill played)
        if card.card_type == CardType.SKILL:
            for e in self.enemies:
                if e.is_alive and e.effects.has("Enrage"):
                    from slay_the_spire.effect import Strength
                    e.effects.add(Strength(e.effects.get_stacks("Enrage")))

        # Curiosity (enemy: gain str when power played)
        if card.card_type == CardType.POWER:
            for e in self.enemies:
                if e.is_alive and e.effects.has("Curiosity"):
                    from slay_the_spire.effect import Strength
                    e.effects.add(Strength(e.effects.get_stacks("Curiosity")))

        # Handle card destination
        if card.card_type == CardType.POWER:
            pass  # Powers don't go anywhere
        elif card.exhaust or (card.card_type == CardType.SKILL and self.player.effects.has("Corruption")):
            self.player.exhaust_pile.append(card)
            self.on_card_exhaust(card)
        else:
            self.player.discard_pile.append(card)

        # Double Tap / Burst / Amplify / Echo Form
        should_replay = False
        if card.card_type == CardType.ATTACK and self.player.effects.has("Double Tap"):
            self.player.effects.reduce("Double Tap")
            should_replay = True
        elif card.card_type == CardType.SKILL and self.player.effects.has("Burst"):
            self.player.effects.reduce("Burst")
            should_replay = True
        elif card.card_type == CardType.POWER and self.player.effects.has("Amplify"):
            self.player.effects.reduce("Amplify")
            should_replay = True

        if should_replay:
            print(f"  {card.name} 再次触发!")
            self.execute_card(card, target, x_amount)

        # Necronomicon: first 2+ cost attack played twice
        if card.card_type == CardType.ATTACK and card.base_cost >= 2:
            necro = self.player.get_relic("Necronomicon")
            if necro and not necro.used_this_combat:
                necro.used_this_combat = True
                print(f"  Necronomicon: {card.name} 再次触发!")
                self.execute_card(card, target, x_amount)

        # Pen Nib consumed
        if card.card_type == CardType.ATTACK and self.player.effects.has("Pen Nib"):
            self.player.effects.remove("Pen Nib")

        # Vigor consumed
        if card.card_type == CardType.ATTACK and self.player.effects.has("Vigor"):
            self.player.effects.remove("Vigor")

        # Phantasmal Killer consumed
        if card.card_type == CardType.ATTACK and self.player.effects.has("Phantasmal Killer"):
            self.player.effects.remove("Phantasmal Killer")

        # Check enemy deaths
        for e in self.enemies:
            if e.hp <= 0 and e.is_alive:
                e.is_alive = False
                e.on_death(self)
                self.on_enemy_death(e)

        return True

    def execute_card(self, card, target, x_amount=0):
        """Execute a card's effects. This is where card logic lives."""
        p = self.player

        # Card effects are stored in card.effects list
        for effect in card.effects:
            action = effect.get("action")

            if action == "damage":
                amount = effect.get("amount", card.damage)
                times = effect.get("times", 1)
                if effect.get("use_x"):
                    times = x_amount
                actual_dmg = p.calc_attack_damage(amount, card)
                if target and card.target == CardTarget.ENEMY:
                    for _ in range(times):
                        self.deal_damage_to_enemy(target, actual_dmg)
                elif card.target == CardTarget.ALL_ENEMIES:
                    for e in self.enemies:
                        if e.is_alive:
                            for _ in range(times):
                                self.deal_damage_to_enemy(e, actual_dmg)

            elif action == "block":
                amount = effect.get("amount", card.block)
                if effect.get("use_x"):
                    amount *= x_amount
                p.gain_block(amount)

            elif action == "apply_effect":
                eff_name = effect["effect"]
                stacks = effect.get("stacks", card.magic)
                if effect.get("use_x"):
                    stacks = x_amount
                tgt = effect.get("target", "enemy")
                if tgt == "enemy" and target:
                    self._apply_effect(target, eff_name, stacks)
                elif tgt == "all_enemies":
                    for e in self.enemies:
                        if e.is_alive:
                            self._apply_effect(e, eff_name, stacks)
                elif tgt == "self":
                    self._apply_effect(p, eff_name, stacks)

            elif action == "draw":
                count = effect.get("amount", 1)
                if effect.get("use_x"):
                    count = x_amount
                p.draw_cards(count)

            elif action == "energy":
                amount = effect.get("amount", 1)
                p.gain_energy(amount)

            elif action == "heal":
                amount = effect.get("amount", 0)
                p.heal(amount)

            elif action == "lose_hp":
                amount = effect.get("amount", 0)
                p.lose_hp(amount)

            elif action == "exhaust_random":
                count = effect.get("amount", 1)
                for _ in range(count):
                    if p.hand:
                        c = random.choice(p.hand)
                        p.hand.remove(c)
                        p.exhaust_pile.append(c)
                        self.on_card_exhaust(c)

            elif action == "add_card":
                card_id = effect.get("card_id")
                to = effect.get("to", "hand")
                count = effect.get("count", 1)
                upgraded = effect.get("upgraded", False)
                if effect.get("use_x"):
                    count = x_amount
                from slay_the_spire.card import create_card
                for _ in range(count):
                    try:
                        new_card = create_card(card_id)
                        if upgraded or (p.effects.has("Master Reality")):
                            new_card.upgrade()
                        if to == "hand" and len(p.hand) < 10:
                            p.hand.append(new_card)
                        elif to == "discard":
                            p.discard_pile.append(new_card)
                        elif to == "draw":
                            p.draw_pile.insert(random.randint(0, len(p.draw_pile)), new_card)
                    except:
                        pass

            elif action == "channel_orb":
                orb_type_str = effect.get("orb_type", "LIGHTNING")
                count = effect.get("count", 1)
                if effect.get("use_x"):
                    count = x_amount
                orb_type = OrbType[orb_type_str]
                for _ in range(count):
                    evoked, new_orb = p.orbs.channel(orb_type)
                    if evoked:
                        self.resolve_evoke(evoked)

            elif action == "evoke":
                count = effect.get("count", 1)
                if effect.get("use_x"):
                    count = x_amount
                for _ in range(count):
                    orb = p.orbs.evoke_first()
                    if orb:
                        self.resolve_evoke(orb)

            elif action == "evoke_all":
                orbs = p.orbs.evoke_all()
                for orb in orbs:
                    self.resolve_evoke(orb)

            elif action == "increase_orb_slots":
                amount = effect.get("amount", 1)
                p.orbs.increase_max(amount)

            elif action == "enter_stance":
                stance_str = effect.get("stance", "NONE")
                new_stance = StanceType[stance_str]
                old, new = p.stance.enter(new_stance)
                if old is not None:
                    self.on_stance_change(old, new)

            elif action == "exit_stance":
                old = p.stance.current
                if old != StanceType.NONE:
                    p.stance.exit_current()
                    self.on_stance_change(old, StanceType.NONE)

            elif action == "scry":
                count = effect.get("amount", 1)
                if p.has_relic("Golden Eye"):
                    count += 2
                self.scry(count)

            elif action == "discard":
                count = effect.get("amount", 1)
                self.prompt_discard(count)

            elif action == "custom":
                func = effect.get("func")
                if func:
                    func(self, p, target, card, x_amount)

    def _apply_effect(self, target, eff_name, stacks):
        """Apply a named effect to a target."""
        # Check Artifact
        from slay_the_spire.effect import EffectType
        eff_module = __import__('slay_the_spire.effect', fromlist=[eff_name])
        factory = getattr(eff_module, eff_name.replace(" ", "_").replace("-", "_"), None)
        if factory:
            eff = factory(stacks)
            if eff.effect_type == EffectType.DEBUFF and hasattr(target, 'effects'):
                if target.effects.has("Artifact"):
                    target.effects.reduce("Artifact")
                    print(f"  {getattr(target, 'name', 'Player')} 的 Artifact 抵消了 {eff_name}!")
                    return
                # Ginger prevents Weak
                if eff_name == "Weak" and hasattr(target, 'has_relic') and target.has_relic("Ginger"):
                    print(f"  Ginger 阻止了虚弱!")
                    return
            target.effects.add(eff)
        else:
            # Fallback: create generic effect
            from slay_the_spire.effect import Effect
            target.effects.add(Effect(eff_name, EffectType.DEBUFF, stacks))

    def apply_effect_to_player(self, eff_name, stacks):
        """Helper to apply effect to player."""
        self._apply_effect(self.player, eff_name, stacks)

    def deal_damage_to_enemy(self, enemy, damage):
        """Deal damage to an enemy (after player attack calc)."""
        if not enemy.is_alive:
            return 0
        # Vulnerable on enemy: +50%
        if enemy.effects.has("Vulnerable"):
            damage = int(damage * 1.5)
        # Lock-On: lightning/dark +50% (handled separately for orbs)
        # The Boot: minimum 5
        if self.player.has_relic("The Boot") and 0 < damage < 5:
            damage = 5
        actual = enemy.take_damage(damage, self)

        # Thorns on enemy
        if enemy.effects.has("Thorns") and actual >= 0:
            self.player.lose_hp(enemy.effects.get_stacks("Thorns"))

        # Sharp Hide
        if enemy.effects.has("Sharp Hide"):
            self.player.lose_hp(enemy.effects.get_stacks("Sharp Hide"))

        # Curl Up: gain block on first hit
        if enemy.effects.has("Curl Up") and actual > 0:
            enemy.gain_block(enemy.effects.get_stacks("Curl Up"))
            enemy.effects.remove("Curl Up")

        # Angry: gain strength when hit
        if enemy.effects.has("Angry") and actual > 0:
            from slay_the_spire.effect import Strength
            enemy.effects.add(Strength(enemy.effects.get_stacks("Angry")))

        # Plated Armor: reduce on unblocked damage
        if enemy.effects.has("Plated Armor") and actual > 0:
            enemy.effects.reduce("Plated Armor")

        # Flight: reduce on hit
        if enemy.effects.has("Flight"):
            enemy.effects.reduce("Flight")

        # Envenom: apply poison on unblocked damage
        if actual > 0 and self.player.effects.has("Envenom"):
            from slay_the_spire.effect import Poison
            enemy.effects.add(Poison(self.player.effects.get_stacks("Envenom")))

        return actual

    def deal_damage_to_player(self, damage, source=None):
        """Deal attack damage to the player."""
        actual = self.player.take_damage(damage)

        if actual > 0:
            # Flame Barrier
            if self.player.effects.has("Flame Barrier") and source:
                source.take_damage(self.player.effects.get_stacks("Flame Barrier"), self)

            # Thorns
            if self.player.effects.has("Thorns") and source:
                source.take_damage(self.player.effects.get_stacks("Thorns"), self)

            # Centennial Puzzle and other on-damage relics
            for relic in self.player.relics:
                relic.on_player_damaged(self.player, actual, self)

            # Runic Cube: draw on HP loss
            if self.player.has_relic("Runic Cube"):
                self.player.draw_cards(1)

            # Rupture: gain strength on HP loss from card
            # (only from own cards, not enemy attacks)

            # Plated Armor reduces
            if self.player.effects.has("Plated Armor"):
                self.player.effects.reduce("Plated Armor")

        if self.player.hp <= 0:
            # Check Fairy in a Bottle
            for i, pot in enumerate(self.player.potions):
                if pot and pot.name == "Fairy in a Bottle":
                    self.player.hp = int(self.player.max_hp * 0.3)
                    self.player.potions[i] = None
                    print(f"  Fairy in a Bottle 救了你! HP恢复到 {self.player.hp}")
                    return actual
            # Check Lizard Tail
            if self.player.has_relic("Lizard Tail"):
                lt = self.player.get_relic("Lizard Tail")
                if not lt.used:
                    lt.used = True
                    self.player.hp = self.player.max_hp // 2
                    print(f"  Lizard Tail 救了你! HP恢复到 {self.player.hp}")
                    return actual
            self.game_over = True

        return actual

    def on_enemy_death(self, enemy):
        """Handle enemy death."""
        print(f"  {enemy.name} 被击败!")
        # Relic: on_enemy_die
        for relic in self.player.relics:
            relic.on_enemy_die(self.player, enemy, self)

    def on_card_exhaust(self, card):
        """Handle card exhaust triggers."""
        # Feel No Pain
        if self.player.effects.has("Feel No Pain"):
            self.player.gain_block_raw(self.player.effects.get_stacks("Feel No Pain"))
        # Dark Embrace
        if self.player.effects.has("Dark Embrace"):
            self.player.draw_cards(self.player.effects.get_stacks("Dark Embrace"))
        # Dead Branch
        if self.player.has_relic("Dead Branch"):
            from slay_the_spire.card import create_card, get_cards_by_color, CardColor
            color_map = {
                "ironclad": CardColor.RED, "silent": CardColor.GREEN,
                "defect": CardColor.BLUE, "watcher": CardColor.PURPLE,
            }
            color = color_map.get(self.player.character_class, CardColor.COLORLESS)
            cards = get_cards_by_color(color)
            if cards:
                new_card = create_card(random.choice(cards))
                if len(self.player.hand) < 10:
                    self.player.hand.append(new_card)
        # Relic: on_card_exhaust
        for relic in self.player.relics:
            relic.on_card_exhaust(self.player, card, self)

    def on_stance_change(self, old_stance, new_stance):
        """Handle stance change triggers."""
        # Calm exit: gain 2 energy
        if old_stance == StanceType.CALM:
            self.player.gain_energy(2)
        # Mental Fortress: gain block
        if self.player.effects.has("Mental Fortress"):
            self.player.gain_block_raw(self.player.effects.get_stacks("Mental Fortress"))
        # Rushdown: draw cards on Wrath enter
        if new_stance == StanceType.WRATH and self.player.effects.has("Rushdown"):
            self.player.draw_cards(self.player.effects.get_stacks("Rushdown"))

    def resolve_evoke(self, orb):
        """Resolve an orb's evoke effect."""
        focus = self.player.effects.get_stacks("Focus")
        if orb.orb_type == OrbType.LIGHTNING:
            dmg = 8 + max(0, focus)
            alive = [e for e in self.enemies if e.is_alive]
            if alive:
                target = random.choice(alive)
                self.deal_damage_to_enemy(target, dmg)
                print(f"  Lightning evoke: 对 {target.name} 造成 {dmg} 伤害")
        elif orb.orb_type == OrbType.FROST:
            blk = 5 + max(0, focus)
            self.player.gain_block_raw(blk)
            print(f"  Frost evoke: 获得 {blk} 格挡")
        elif orb.orb_type == OrbType.DARK:
            dmg = orb.dark_damage
            alive = [e for e in self.enemies if e.is_alive]
            if alive:
                target = min(alive, key=lambda e: e.hp)
                self.deal_damage_to_enemy(target, dmg)
                print(f"  Dark evoke: 对 {target.name} 造成 {dmg} 伤害")
        elif orb.orb_type == OrbType.PLASMA:
            self.player.gain_energy(2)
            print(f"  Plasma evoke: 获得 2 能量")

    def scry(self, count):
        """Scry: look at top N cards, discard any."""
        if not self.player.draw_pile:
            return
        cards = self.player.draw_pile[-count:]
        if not cards:
            return
        print(f"  Scry - 查看顶部 {len(cards)} 张牌:")
        for i, c in enumerate(cards):
            print(f"    {i + 1}. {c.short_desc()}")
        print("  输入要丢弃的牌号(逗号分隔), 或回车跳过:")
        choice = ui.get_input()
        if choice:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                for idx in sorted(indices, reverse=True):
                    if 0 <= idx < len(cards):
                        card = cards[idx]
                        self.player.draw_pile.remove(card)
                        self.player.discard_pile.append(card)
            except ValueError:
                pass

    def prompt_discard(self, count):
        """Prompt player to discard cards."""
        for _ in range(count):
            if not self.player.hand:
                break
            print("选择要弃置的牌:")
            for i, c in enumerate(self.player.hand):
                print(f"  {i + 1}. {c.short_desc()}")
            choice = ui.get_input()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.player.hand):
                    card = self.player.hand.pop(idx)
                    self.player.discard_pile.append(card)
            except ValueError:
                pass

    def handle_potion_use(self):
        """Handle potion usage during combat."""
        ui.display_potions(self.player.potions)
        print("选择药水编号使用, 或 0 取消:")
        choice = ui.get_input()
        try:
            idx = int(choice) - 1
            if idx == -1:
                return
            if 0 <= idx < self.player.max_potions:
                potion = self.player.potions[idx]
                if potion is None:
                    print("  该药水槽为空!")
                    return
                target = None
                if potion.requires_target:
                    alive = [e for e in self.enemies if e.is_alive]
                    if len(alive) == 1:
                        target = alive[0]
                    else:
                        print("选择目标:")
                        for i, e in enumerate(alive):
                            print(f"  {i + 1}. {e.name}")
                        t_choice = ui.get_input()
                        try:
                            t_idx = int(t_choice) - 1
                            if 0 <= t_idx < len(alive):
                                target = alive[t_idx]
                        except ValueError:
                            return
                potion.use(self.player, self, target)
                self.player.potions[idx] = None
                print(f"  使用了 {potion.name}!")
                # Relic: on_potion_use
                for relic in self.player.relics:
                    relic.on_potion_use(self.player, potion, self)
        except ValueError:
            pass

    def is_finished(self):
        """Check if combat is over."""
        if self.escaped:
            self.victory = True
            return True
        if self.game_over or self.player.hp <= 0:
            self.game_over = True
            return True
        if all(not e.is_alive for e in self.enemies):
            self.victory = True
            return True
        return False

    def cleanup(self):
        """Post-combat cleanup."""
        if self.victory:
            # Relic: on_combat_end
            for relic in self.player.relics:
                relic.on_combat_end(self.player, self)
