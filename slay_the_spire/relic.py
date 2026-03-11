"""Relic system for Slay the Spire - all ~170 relics."""
from enum import Enum, auto


class RelicRarity(Enum):
    STARTER = auto()
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    BOSS = auto()
    SHOP = auto()
    EVENT = auto()
    SPECIAL = auto()


class Relic:
    """Base class for relics."""

    def __init__(self, name, rarity, description="", counter=-1, color=None):
        self.name = name
        self.rarity = rarity
        self.description = description
        self.counter = counter  # -1 = no counter, 0+ = active counter
        self.color = color  # None = any class, "ironclad"/"silent"/"defect"/"watcher"
        self.enabled = True

    def on_obtain(self, player):
        """Called when relic is obtained."""
        pass

    def on_combat_start(self, player, combat):
        pass

    def on_turn_start(self, player, combat):
        pass

    def on_turn_end(self, player, combat):
        pass

    def on_card_play(self, player, card, combat):
        pass

    def on_attack_damage(self, player, target, damage, combat):
        pass

    def on_player_damaged(self, player, damage, combat):
        pass

    def on_enemy_die(self, player, enemy, combat):
        pass

    def on_combat_end(self, player, combat):
        pass

    def on_rest(self, player):
        pass

    def on_card_exhaust(self, player, card, combat):
        pass

    def on_block_gain(self, player, amount, combat):
        return amount

    def on_potion_use(self, player, potion, combat):
        pass

    def on_chest_open(self, player):
        pass

    def on_enter_shop(self, player):
        pass

    def on_card_reward(self, player, cards):
        return cards

    def __repr__(self):
        if self.counter >= 0:
            return f"{self.name}({self.counter})"
        return self.name


# ===================================================
# STARTER RELICS
# ===================================================

class BurningBlood(Relic):
    def __init__(self):
        super().__init__("Burning Blood", RelicRarity.STARTER,
                         "At the end of combat, heal 6 HP.", color="ironclad")

    def on_combat_end(self, player, combat):
        player.heal(6)


class RingOfTheSnake(Relic):
    def __init__(self):
        super().__init__("Ring of the Snake", RelicRarity.STARTER,
                         "At the start of each combat, draw 2 additional cards.", color="silent")

    def on_combat_start(self, player, combat):
        player.draw_cards(2)


class CrackedCore(Relic):
    def __init__(self):
        super().__init__("Cracked Core", RelicRarity.STARTER,
                         "At the start of each combat, Channel 1 Lightning.", color="defect")

    def on_combat_start(self, player, combat):
        from slay_the_spire.orb import OrbType
        player.orbs.channel(OrbType.LIGHTNING)


class PureWater(Relic):
    def __init__(self):
        super().__init__("Pure Water", RelicRarity.STARTER,
                         "At the start of each combat, add a Miracle to your hand.", color="watcher")

    def on_combat_start(self, player, combat):
        from slay_the_spire.card import create_card
        try:
            miracle = create_card("miracle")
            player.hand.append(miracle)
        except:
            pass


# ===================================================
# COMMON RELICS
# ===================================================

class Anchor(Relic):
    def __init__(self):
        super().__init__("Anchor", RelicRarity.COMMON, "Start each combat with 10 Block.")

    def on_combat_start(self, player, combat):
        player.gain_block_raw(10)


class AncientTeaSet(Relic):
    def __init__(self):
        super().__init__("Ancient Tea Set", RelicRarity.COMMON,
                         "Whenever you enter a Rest Site, start the next combat with 2 extra Energy.")
        self.triggered = False

    def on_rest(self, player):
        self.triggered = True

    def on_combat_start(self, player, combat):
        if self.triggered:
            player.gain_energy(2)
            self.triggered = False


class ArtOfWar(Relic):
    def __init__(self):
        super().__init__("Art of War", RelicRarity.COMMON,
                         "If you do not play an Attack during your turn, gain 1 extra Energy next turn.")

    def on_turn_end(self, player, combat):
        if player.attacks_played_this_turn == 0:
            from slay_the_spire.effect import Energized
            player.effects.add(Energized(1))


class BagOfMarbles(Relic):
    def __init__(self):
        super().__init__("Bag of Marbles", RelicRarity.COMMON,
                         "At the start of each combat, apply 1 Vulnerable to ALL enemies.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Vulnerable
        for e in combat.enemies:
            e.effects.add(Vulnerable(1))


class BagOfPreparation(Relic):
    def __init__(self):
        super().__init__("Bag of Preparation", RelicRarity.COMMON,
                         "At the start of each combat, draw 2 additional cards.")

    def on_combat_start(self, player, combat):
        player.draw_cards(2)


class BloodVial(Relic):
    def __init__(self):
        super().__init__("Blood Vial", RelicRarity.COMMON,
                         "At the start of each combat, heal 2 HP.")

    def on_combat_start(self, player, combat):
        player.heal(2)


class BronzeScales(Relic):
    def __init__(self):
        super().__init__("Bronze Scales", RelicRarity.COMMON,
                         "Start each combat with 3 Thorns.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Thorns
        player.effects.add(Thorns(3))


class CentennialPuzzle(Relic):
    def __init__(self):
        super().__init__("Centennial Puzzle", RelicRarity.COMMON,
                         "The first time you lose HP in combat, draw 3 cards.")
        self.triggered = False

    def on_combat_start(self, player, combat):
        self.triggered = False

    def on_player_damaged(self, player, damage, combat):
        if not self.triggered and damage > 0:
            self.triggered = True
            player.draw_cards(3)


class CeramicFish(Relic):
    def __init__(self):
        super().__init__("Ceramic Fish", RelicRarity.COMMON,
                         "Whenever you add a card to your deck, gain 9 Gold.")


class DreamCatcher(Relic):
    def __init__(self):
        super().__init__("Dream Catcher", RelicRarity.COMMON,
                         "Whenever you rest, you may add a card to your deck.")


class HappyFlower(Relic):
    def __init__(self):
        super().__init__("Happy Flower", RelicRarity.COMMON,
                         "Every 3 turns, gain 1 Energy.", counter=0)

    def on_turn_start(self, player, combat):
        self.counter += 1
        if self.counter >= 3:
            self.counter = 0
            player.gain_energy(1)


class JuzuBracelet(Relic):
    def __init__(self):
        super().__init__("Juzu Bracelet", RelicRarity.COMMON,
                         "Regular enemy combats are no longer encountered in ? rooms.")


class Lantern(Relic):
    def __init__(self):
        super().__init__("Lantern", RelicRarity.COMMON,
                         "Gain 1 Energy on the first turn of each combat.")

    def on_combat_start(self, player, combat):
        player.gain_energy(1)


class MawBank(Relic):
    def __init__(self):
        super().__init__("Maw Bank", RelicRarity.COMMON,
                         "Whenever you climb a floor, gain 12 Gold. Loses this effect when you spend gold at a Shop.")
        self.active = True


class MealTicket(Relic):
    def __init__(self):
        super().__init__("Meal Ticket", RelicRarity.COMMON,
                         "Whenever you enter a Shop, heal 15 HP.")

    def on_enter_shop(self, player):
        player.heal(15)


class Nunchaku(Relic):
    def __init__(self):
        super().__init__("Nunchaku", RelicRarity.COMMON,
                         "Every time you play 10 Attacks, gain 1 Energy.", counter=0)

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.ATTACK:
            self.counter += 1
            if self.counter >= 10:
                self.counter = 0
                player.gain_energy(1)


class OddlySmoothStone(Relic):
    def __init__(self):
        super().__init__("Oddly Smooth Stone", RelicRarity.COMMON,
                         "Start each combat with 1 Dexterity.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Dexterity
        player.effects.add(Dexterity(1))


class Orichalcum(Relic):
    def __init__(self):
        super().__init__("Orichalcum", RelicRarity.COMMON,
                         "If you end your turn without Block, gain 6 Block.")

    def on_turn_end(self, player, combat):
        if player.block == 0:
            player.gain_block_raw(6)


class PenNib(Relic):
    def __init__(self):
        super().__init__("Pen Nib", RelicRarity.COMMON,
                         "Every 10th Attack you play deals double damage.", counter=0)

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.ATTACK:
            self.counter += 1
            if self.counter >= 10:
                self.counter = 0


class PotionBelt(Relic):
    def __init__(self):
        super().__init__("Potion Belt", RelicRarity.COMMON,
                         "Upon pickup, gain 2 extra potion slots.")

    def on_obtain(self, player):
        player.max_potions += 2
        player.potions.extend([None, None])


class PreservedInsect(Relic):
    def __init__(self):
        super().__init__("Preserved Insect", RelicRarity.COMMON,
                         "Enemies in Elite combats have 25% less HP.")


class Regal_Pillow(Relic):
    def __init__(self):
        super().__init__("Regal Pillow", RelicRarity.COMMON,
                         "Heal an additional 15 HP when you Rest.")


class SmilingMask(Relic):
    def __init__(self):
        super().__init__("Smiling Mask", RelicRarity.COMMON,
                         "The cost to remove cards at the Shop is always 50 Gold.")


class Strawberry(Relic):
    def __init__(self):
        super().__init__("Strawberry", RelicRarity.COMMON,
                         "Upon pickup, gain 7 Max HP.")

    def on_obtain(self, player):
        player.max_hp += 7
        player.hp += 7


class TheBoot(Relic):
    def __init__(self):
        super().__init__("The Boot", RelicRarity.COMMON,
                         "Whenever you would deal 4 or less unblocked Attack damage, deal 5 instead.")


class TinyChest(Relic):
    def __init__(self):
        super().__init__("Tiny Chest", RelicRarity.COMMON,
                         "Every 4th ? room is a Treasure room.", counter=0)


class ToyOrnithopter(Relic):
    def __init__(self):
        super().__init__("Toy Ornithopter", RelicRarity.COMMON,
                         "Whenever you use a potion, heal 5 HP.")

    def on_potion_use(self, player, potion, combat):
        player.heal(5)


class Vajra(Relic):
    def __init__(self):
        super().__init__("Vajra", RelicRarity.COMMON,
                         "Start each combat with 1 Strength.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Strength
        player.effects.add(Strength(1))


class WarPaint(Relic):
    def __init__(self):
        super().__init__("War Paint", RelicRarity.COMMON,
                         "Upon pickup, Upgrade 2 random Skills.")


class Whetstone(Relic):
    def __init__(self):
        super().__init__("Whetstone", RelicRarity.COMMON,
                         "Upon pickup, Upgrade 2 random Attacks.")


# ===================================================
# UNCOMMON RELICS
# ===================================================

class BlueCandle(Relic):
    def __init__(self):
        super().__init__("Blue Candle", RelicRarity.UNCOMMON,
                         "Curse cards can now be played. Playing a Curse exhausts it and deals 1 damage to you.")


class BottledFlame(Relic):
    def __init__(self):
        super().__init__("Bottled Flame", RelicRarity.UNCOMMON,
                         "Upon pickup, choose an Attack. Start each combat with it in your hand.")
        self.card = None


class BottledLightning(Relic):
    def __init__(self):
        super().__init__("Bottled Lightning", RelicRarity.UNCOMMON,
                         "Upon pickup, choose a Skill. Start each combat with it in your hand.")
        self.card = None


class BottledTornado(Relic):
    def __init__(self):
        super().__init__("Bottled Tornado", RelicRarity.UNCOMMON,
                         "Upon pickup, choose a Power. Start each combat with it in your hand.")
        self.card = None


class DarkstonePeriapt(Relic):
    def __init__(self):
        super().__init__("Darkstone Periapt", RelicRarity.UNCOMMON,
                         "Whenever you obtain a Curse, gain 6 Max HP.")


class EternalFeather(Relic):
    def __init__(self):
        super().__init__("Eternal Feather", RelicRarity.UNCOMMON,
                         "Whenever you enter a Rest Site, heal 3 HP for every 5 cards in your deck.")

    def on_rest(self, player):
        heal = (len(player.deck) // 5) * 3
        player.heal(heal)


class FrozenEgg(Relic):
    def __init__(self):
        super().__init__("Frozen Egg", RelicRarity.UNCOMMON,
                         "Whenever you add a Power to your deck, it is Upgraded.")


class GremlinHorn(Relic):
    def __init__(self):
        super().__init__("Gremlin Horn", RelicRarity.UNCOMMON,
                         "Whenever a non-Minion enemy dies, gain 1 Energy and draw 1 card.")

    def on_enemy_die(self, player, enemy, combat):
        if not enemy.is_minion:
            player.gain_energy(1)
            player.draw_cards(1)


class HornCleat(Relic):
    def __init__(self):
        super().__init__("Horn Cleat", RelicRarity.UNCOMMON,
                         "At the start of your 2nd turn, gain 14 Block.")

    def on_turn_start(self, player, combat):
        if player.cards_played_this_combat == 0 and combat and combat.turn == 2:
            player.gain_block_raw(14)


class InkBottle(Relic):
    def __init__(self):
        super().__init__("Ink Bottle", RelicRarity.UNCOMMON,
                         "Every 10 cards you play, draw 1 card.", counter=0)

    def on_card_play(self, player, card, combat):
        self.counter += 1
        if self.counter >= 10:
            self.counter = 0
            player.draw_cards(1)


class Kunai(Relic):
    def __init__(self):
        super().__init__("Kunai", RelicRarity.UNCOMMON,
                         "Every time you play 3 Attacks in a single turn, gain 1 Dexterity.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.ATTACK:
            if player.attacks_played_this_turn > 0 and player.attacks_played_this_turn % 3 == 0:
                from slay_the_spire.effect import Dexterity
                player.effects.add(Dexterity(1))


class LetterOpener(Relic):
    def __init__(self):
        super().__init__("Letter Opener", RelicRarity.UNCOMMON,
                         "Every time you play 3 Skills in a single turn, deal 5 damage to ALL enemies.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.SKILL:
            if player.skills_played_this_turn > 0 and player.skills_played_this_turn % 3 == 0:
                if combat:
                    for e in combat.enemies:
                        if e.is_alive:
                            e.take_damage(5, combat)


class Matryoshka(Relic):
    def __init__(self):
        super().__init__("Matryoshka", RelicRarity.UNCOMMON,
                         "The next 2 non-boss chests contain 2 relics.", counter=2)


class MeatOnTheBone(Relic):
    def __init__(self):
        super().__init__("Meat on the Bone", RelicRarity.UNCOMMON,
                         "If your HP is at or below 50% at the end of combat, heal 12 HP.")

    def on_combat_end(self, player, combat):
        if player.hp <= player.max_hp // 2:
            player.heal(12)


class MercuryHourglass(Relic):
    def __init__(self):
        super().__init__("Mercury Hourglass", RelicRarity.UNCOMMON,
                         "At the start of each turn, deal 3 damage to ALL enemies.")

    def on_turn_start(self, player, combat):
        if combat:
            for e in combat.enemies:
                if e.is_alive:
                    e.take_damage(3, combat)


class MoltenEgg(Relic):
    def __init__(self):
        super().__init__("Molten Egg", RelicRarity.UNCOMMON,
                         "Whenever you add an Attack to your deck, it is Upgraded.")


class MummifiedHand(Relic):
    def __init__(self):
        super().__init__("Mummified Hand", RelicRarity.UNCOMMON,
                         "Whenever you play a Power, a random card in your hand costs 0 this turn.")

    def on_card_play(self, player, card, combat):
        import random
        from slay_the_spire.card import CardType
        if card.card_type == CardType.POWER:
            non_zero = [c for c in player.hand if c.cost_for_turn > 0]
            if non_zero:
                random.choice(non_zero).cost_for_turn = 0


class OrnamentalFan(Relic):
    def __init__(self):
        super().__init__("Ornamental Fan", RelicRarity.UNCOMMON,
                         "Every time you play 3 Attacks in a single turn, gain 4 Block.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.ATTACK:
            if player.attacks_played_this_turn > 0 and player.attacks_played_this_turn % 3 == 0:
                player.gain_block_raw(4)


class Pantograph(Relic):
    def __init__(self):
        super().__init__("Pantograph", RelicRarity.UNCOMMON,
                         "At the start of Boss combats, heal 25 HP.")

    def on_combat_start(self, player, combat):
        if combat and combat.is_boss:
            player.heal(25)


class Pear(Relic):
    def __init__(self):
        super().__init__("Pear", RelicRarity.UNCOMMON,
                         "Upon pickup, gain 10 Max HP.")

    def on_obtain(self, player):
        player.max_hp += 10
        player.hp += 10


class QuestionCard(Relic):
    def __init__(self):
        super().__init__("Question Card", RelicRarity.UNCOMMON,
                         "Future card rewards have 1 extra option.")


class Shuriken(Relic):
    def __init__(self):
        super().__init__("Shuriken", RelicRarity.UNCOMMON,
                         "Every time you play 3 Attacks in a single turn, gain 1 Strength.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.ATTACK:
            if player.attacks_played_this_turn > 0 and player.attacks_played_this_turn % 3 == 0:
                from slay_the_spire.effect import Strength
                player.effects.add(Strength(1))


class SingingBowl(Relic):
    def __init__(self):
        super().__init__("Singing Bowl", RelicRarity.UNCOMMON,
                         "When adding cards to your deck, you may gain 2 Max HP instead.")


class StrikeDummy(Relic):
    def __init__(self):
        super().__init__("Strike Dummy", RelicRarity.UNCOMMON,
                         "Whenever you play a card that has \"Strike\" in its name, deal 3 additional damage.")


class Sundial(Relic):
    def __init__(self):
        super().__init__("Sundial", RelicRarity.UNCOMMON,
                         "Every 3 times you shuffle your draw pile, gain 2 Energy.", counter=0)


class SymbioticVirus(Relic):
    def __init__(self):
        super().__init__("Symbiotic Virus", RelicRarity.UNCOMMON,
                         "At the start of each combat, Channel 1 Dark.", color="defect")

    def on_combat_start(self, player, combat):
        from slay_the_spire.orb import OrbType
        player.orbs.channel(OrbType.DARK)


class TeardropLocket(Relic):
    def __init__(self):
        super().__init__("Teardrop Locket", RelicRarity.UNCOMMON,
                         "At the start of each combat, enter Calm.", color="watcher")

    def on_combat_start(self, player, combat):
        from slay_the_spire.stance import StanceType
        player.stance.enter(StanceType.CALM)


class TheCorier(Relic):
    def __init__(self):
        super().__init__("The Courier", RelicRarity.UNCOMMON,
                         "The Shop always has a card removal option and prices are 20% reduced.")


class ToxicEgg(Relic):
    def __init__(self):
        super().__init__("Toxic Egg", RelicRarity.UNCOMMON,
                         "Whenever you add a Skill to your deck, it is Upgraded.")


class WhiteBeastStatue(Relic):
    def __init__(self):
        super().__init__("White Beast Statue", RelicRarity.UNCOMMON,
                         "Potions always drop after combat.")


# ===================================================
# RARE RELICS
# ===================================================

class BirdFacedUrn(Relic):
    def __init__(self):
        super().__init__("Bird-Faced Urn", RelicRarity.RARE,
                         "Whenever you play a Power, heal 2 HP.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if card.card_type == CardType.POWER:
            player.heal(2)


class Calipers(Relic):
    def __init__(self):
        super().__init__("Calipers", RelicRarity.RARE,
                         "At the start of your turn, lose 15 Block instead of all Block.")


class CaptainsWheel(Relic):
    def __init__(self):
        super().__init__("Captain's Wheel", RelicRarity.RARE,
                         "At the start of your 3rd turn, gain 18 Block.")

    def on_turn_start(self, player, combat):
        if combat and combat.turn == 3:
            player.gain_block_raw(18)


class DeadBranch(Relic):
    def __init__(self):
        super().__init__("Dead Branch", RelicRarity.RARE,
                         "Whenever you Exhaust a card, add a random card to your hand.")


class DuVuDoll(Relic):
    def __init__(self):
        super().__init__("Du-Vu Doll", RelicRarity.RARE,
                         "For each Curse in your deck, start each combat with 1 additional Strength.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.card import CardType
        from slay_the_spire.effect import Strength
        curse_count = sum(1 for c in player.deck if c.card_type == CardType.CURSE)
        if curse_count > 0:
            player.effects.add(Strength(curse_count))


class FossilizedHelix(Relic):
    def __init__(self):
        super().__init__("Fossilized Helix", RelicRarity.RARE,
                         "Prevent the first time you would lose HP in each combat.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Buffer
        player.effects.add(Buffer(1))


class GamblingChip(Relic):
    def __init__(self):
        super().__init__("Gambling Chip", RelicRarity.RARE,
                         "At the start of each combat, discard any number of cards then draw that many.")


class Ginger(Relic):
    def __init__(self):
        super().__init__("Ginger", RelicRarity.RARE,
                         "You can no longer become Weakened.")


class Girya(Relic):
    def __init__(self):
        super().__init__("Girya", RelicRarity.RARE,
                         "You can now gain Strength at Rest Sites. (Up to 3 times.)", counter=0)


class IceCream(Relic):
    def __init__(self):
        super().__init__("Ice Cream", RelicRarity.RARE,
                         "Energy is now conserved between turns.")


class IncenseBurner(Relic):
    def __init__(self):
        super().__init__("Incense Burner", RelicRarity.RARE,
                         "Every 6 turns, gain 1 Intangible.", counter=0)

    def on_turn_end(self, player, combat):
        self.counter += 1
        if self.counter >= 6:
            self.counter = 0
            from slay_the_spire.effect import Intangible
            player.effects.add(Intangible(1))


class LizardTail(Relic):
    def __init__(self):
        super().__init__("Lizard Tail", RelicRarity.RARE,
                         "When you would die, heal to 50% HP instead. Works once.")
        self.used = False


class Mango(Relic):
    def __init__(self):
        super().__init__("Mango", RelicRarity.RARE,
                         "Upon pickup, gain 14 Max HP.")

    def on_obtain(self, player):
        player.max_hp += 14
        player.hp += 14


class OldCoin(Relic):
    def __init__(self):
        super().__init__("Old Coin", RelicRarity.RARE,
                         "Upon pickup, gain 300 Gold.")

    def on_obtain(self, player):
        player.gold += 300


class PeacePipe(Relic):
    def __init__(self):
        super().__init__("Peace Pipe", RelicRarity.RARE,
                         "You can now remove cards at Rest Sites.")


class Pocketwatch(Relic):
    def __init__(self):
        super().__init__("Pocketwatch", RelicRarity.RARE,
                         "Whenever you play 3 or fewer cards on your turn, draw 3 extra next turn.")

    def on_turn_end(self, player, combat):
        if player.cards_played_this_turn <= 3:
            from slay_the_spire.effect import Draw_Card
            player.effects.add(Draw_Card(3))


class PrayerWheel(Relic):
    def __init__(self):
        super().__init__("Prayer Wheel", RelicRarity.RARE,
                         "Normal enemy combats reward you with an extra card choice.")


class Shovel(Relic):
    def __init__(self):
        super().__init__("Shovel", RelicRarity.RARE,
                         "You can now Dig for relics at Rest Sites.")


class StoneCalendar(Relic):
    def __init__(self):
        super().__init__("Stone Calendar", RelicRarity.RARE,
                         "At the end of turn 7, deal 52 damage to ALL enemies.", counter=0)

    def on_turn_end(self, player, combat):
        self.counter += 1
        if self.counter >= 7 and combat:
            for e in combat.enemies:
                if e.is_alive:
                    e.take_damage(52, combat)


class ThreadAndNeedle(Relic):
    def __init__(self):
        super().__init__("Thread and Needle", RelicRarity.RARE,
                         "Start each combat with 4 Plated Armor.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Plated_Armor
        player.effects.add(Plated_Armor(4))


class Torii(Relic):
    def __init__(self):
        super().__init__("Torii", RelicRarity.RARE,
                         "Whenever you would receive 5 or less unblocked Attack damage, reduce it to 1.")


class TungstenRod(Relic):
    def __init__(self):
        super().__init__("Tungsten Rod", RelicRarity.RARE,
                         "Whenever you would lose HP, lose 1 less.")


# ===================================================
# BOSS RELICS
# ===================================================

class Astrolabe(Relic):
    def __init__(self):
        super().__init__("Astrolabe", RelicRarity.BOSS,
                         "Upon pickup, choose and Transform 3 cards, then Upgrade them.")


class BlackStar(Relic):
    def __init__(self):
        super().__init__("Black Star", RelicRarity.BOSS,
                         "Elites drop 2 relics instead of 1.")


class BustedCrown(Relic):
    def __init__(self):
        super().__init__("Busted Crown", RelicRarity.BOSS,
                         "Gain 1 Energy at the start of each turn. Card reward options are reduced by 2.")

    def on_obtain(self, player):
        player.max_energy += 1


class CallingBell(Relic):
    def __init__(self):
        super().__init__("Calling Bell", RelicRarity.BOSS,
                         "Upon pickup, gain a Curse and 3 relics.")


class CoffeeDripper(Relic):
    def __init__(self):
        super().__init__("Coffee Dripper", RelicRarity.BOSS,
                         "Gain 1 Energy at the start of each turn. You can no longer rest at Rest Sites.")

    def on_obtain(self, player):
        player.max_energy += 1


class CursedKey(Relic):
    def __init__(self):
        super().__init__("Cursed Key", RelicRarity.BOSS,
                         "Gain 1 Energy at the start of each turn. Gain a Curse when opening chests.")

    def on_obtain(self, player):
        player.max_energy += 1


class Ectoplasm(Relic):
    def __init__(self):
        super().__init__("Ectoplasm", RelicRarity.BOSS,
                         "Gain 1 Energy at the start of each turn. You can no longer gain Gold.")

    def on_obtain(self, player):
        player.max_energy += 1


class EmptyCage(Relic):
    def __init__(self):
        super().__init__("Empty Cage", RelicRarity.BOSS,
                         "Upon pickup, remove 2 cards from your deck.")


class FusionHammer(Relic):
    def __init__(self):
        super().__init__("Fusion Hammer", RelicRarity.BOSS,
                         "Gain 1 Energy at the start of each turn. You can no longer Smith at Rest Sites.")

    def on_obtain(self, player):
        player.max_energy += 1


class HolyWater(Relic):
    def __init__(self):
        super().__init__("Holy Water", RelicRarity.BOSS,
                         "At the start of each combat, add 3 Miracles to your hand.", color="watcher")

    def on_combat_start(self, player, combat):
        from slay_the_spire.card import create_card
        for _ in range(3):
            try:
                m = create_card("miracle")
                player.hand.append(m)
            except:
                pass


class MarkOfPain(Relic):
    def __init__(self):
        super().__init__("Mark of Pain", RelicRarity.BOSS,
                         "Gain 1 Energy. Start combat with 2 Wounds in draw pile.", color="ironclad")

    def on_obtain(self, player):
        player.max_energy += 1


class Pandoras_Box(Relic):
    def __init__(self):
        super().__init__("Pandora's Box", RelicRarity.BOSS,
                         "Transform all Strikes and Defends.")


class PhilosopherStone(Relic):
    def __init__(self):
        super().__init__("Philosopher's Stone", RelicRarity.BOSS,
                         "Gain 1 Energy. ALL enemies start with 1 Strength.")

    def on_obtain(self, player):
        player.max_energy += 1

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Strength
        for e in combat.enemies:
            e.effects.add(Strength(1))


class RunicCube(Relic):
    def __init__(self):
        super().__init__("Runic Cube", RelicRarity.BOSS,
                         "Whenever you lose HP, draw 1 card.")


class RunicDome(Relic):
    def __init__(self):
        super().__init__("Runic Dome", RelicRarity.BOSS,
                         "Gain 1 Energy. You can no longer see enemy Intents.")

    def on_obtain(self, player):
        player.max_energy += 1


class RunicPyramid(Relic):
    def __init__(self):
        super().__init__("Runic Pyramid", RelicRarity.BOSS,
                         "At the end of your turn, you no longer discard your hand.")


class SacredBark(Relic):
    def __init__(self):
        super().__init__("Sacred Bark", RelicRarity.BOSS,
                         "Double the effectiveness of potions.")


class SlaversCollar(Relic):
    def __init__(self):
        super().__init__("Slaver's Collar", RelicRarity.BOSS,
                         "During Boss and Elite combats, gain 1 Energy at the start of each turn.")

    def on_combat_start(self, player, combat):
        if combat and (combat.is_boss or combat.is_elite):
            player.max_energy += 1

    def on_combat_end(self, player, combat):
        if combat and (combat.is_boss or combat.is_elite):
            player.max_energy -= 1


class SneckoEye(Relic):
    def __init__(self):
        super().__init__("Snecko Eye", RelicRarity.BOSS,
                         "Draw 2 additional cards each turn. All card costs are randomized.")

    def on_obtain(self, player):
        player.base_draw += 2


class Sozu(Relic):
    def __init__(self):
        super().__init__("Sozu", RelicRarity.BOSS,
                         "Gain 1 Energy. You can no longer obtain potions.")

    def on_obtain(self, player):
        player.max_energy += 1


class TinyHouse(Relic):
    def __init__(self):
        super().__init__("Tiny House", RelicRarity.BOSS,
                         "Gain 50 Gold, 5 Max HP, 1 potion, 1 card, Upgrade 1 random card.")

    def on_obtain(self, player):
        player.gold += 50
        player.max_hp += 5
        player.hp += 5


class VelvetChoker(Relic):
    def __init__(self):
        super().__init__("Velvet Choker", RelicRarity.BOSS,
                         "Gain 1 Energy. You cannot play more than 6 cards per turn.", counter=0)

    def on_obtain(self, player):
        player.max_energy += 1

    def on_turn_start(self, player, combat):
        self.counter = 0

    def on_card_play(self, player, card, combat):
        self.counter += 1


class WristBlade(Relic):
    def __init__(self):
        super().__init__("Wrist Blade", RelicRarity.BOSS,
                         "Attacks that cost 0 deal 3 additional damage.", color="silent")


# ===================================================
# SHOP RELICS
# ===================================================

class Cauldron(Relic):
    def __init__(self):
        super().__init__("Cauldron", RelicRarity.SHOP,
                         "Upon pickup, gain 5 random potions.")


class ChemicalX(Relic):
    def __init__(self):
        super().__init__("Chemical X", RelicRarity.SHOP,
                         "Whenever you play an X-cost card, gain 2 more to its effect.")


class ClockworkSouvenir(Relic):
    def __init__(self):
        super().__init__("Clockwork Souvenir", RelicRarity.SHOP,
                         "At the start of each combat, gain 1 Artifact.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Artifact
        player.effects.add(Artifact(1))


class DollysMirror(Relic):
    def __init__(self):
        super().__init__("Dolly's Mirror", RelicRarity.SHOP,
                         "Upon pickup, obtain a copy of a card in your deck.")


class FrozenEye(Relic):
    def __init__(self):
        super().__init__("Frozen Eye", RelicRarity.SHOP,
                         "You can now see the order of your draw pile.")


class HandDrill(Relic):
    def __init__(self):
        super().__init__("Hand Drill", RelicRarity.SHOP,
                         "When an enemy's Block is broken, apply 2 Vulnerable.")


class LeesWaffle(Relic):
    def __init__(self):
        super().__init__("Lee's Waffle", RelicRarity.SHOP,
                         "Upon pickup, gain 7 Max HP and heal to full.")

    def on_obtain(self, player):
        player.max_hp += 7
        player.hp = player.max_hp


class MedicalKit(Relic):
    def __init__(self):
        super().__init__("Medical Kit", RelicRarity.SHOP,
                         "Status cards can now be played. Playing a Status exhausts it.")


class MembershipCard(Relic):
    def __init__(self):
        super().__init__("Membership Card", RelicRarity.SHOP,
                         "50% off all purchases at the Shop.")


class OrangePellets(Relic):
    def __init__(self):
        super().__init__("Orange Pellets", RelicRarity.SHOP,
                         "Whenever you play a Power, Skill, and Attack in the same turn, remove all debuffs.")

    def on_card_play(self, player, card, combat):
        from slay_the_spire.card import CardType
        if (player.attacks_played_this_turn > 0 and
            player.skills_played_this_turn > 0 and
            player.powers_played_this_turn > 0):
            debuffs = list(player.effects.get_debuffs().keys())
            for d in debuffs:
                player.effects.remove(d)


class Orrery(Relic):
    def __init__(self):
        super().__init__("Orrery", RelicRarity.SHOP,
                         "Upon pickup, choose and add 5 cards to your deck.")


class PrismaticShard(Relic):
    def __init__(self):
        super().__init__("Prismatic Shard", RelicRarity.SHOP,
                         "Card rewards can now include cards from any color.")


class SlingOfCourage(Relic):
    def __init__(self):
        super().__init__("Sling of Courage", RelicRarity.SHOP,
                         "Start Elite combats with 2 Strength.")

    def on_combat_start(self, player, combat):
        if combat and combat.is_elite:
            from slay_the_spire.effect import Strength
            player.effects.add(Strength(2))


class StrangeSpoon(Relic):
    def __init__(self):
        super().__init__("Strange Spoon", RelicRarity.SHOP,
                         "Cards which Exhaust will instead 50% of the time be reshuffled into your draw pile.")


class TheAbacus(Relic):
    def __init__(self):
        super().__init__("The Abacus", RelicRarity.SHOP,
                         "Whenever you shuffle, gain 6 Block.")


class Toolbox(Relic):
    def __init__(self):
        super().__init__("Toolbox", RelicRarity.SHOP,
                         "At the start of each combat, choose 1 of 3 Colorless cards to add to your hand.")


# ===================================================
# EVENT RELICS
# ===================================================

class BloodyIdol(Relic):
    def __init__(self):
        super().__init__("Bloody Idol", RelicRarity.EVENT,
                         "Whenever you gain Gold, heal 5 HP.")


class CultistHeadpiece(Relic):
    def __init__(self):
        super().__init__("Cultist Headpiece", RelicRarity.EVENT,
                         "Caw caw!")


class Enchiridion(Relic):
    def __init__(self):
        super().__init__("Enchiridion", RelicRarity.EVENT,
                         "At the start of each combat, add a random Power to your hand. It costs 0 this turn.")


class FaceOfCleric(Relic):
    def __init__(self):
        super().__init__("Face of Cleric", RelicRarity.EVENT,
                         "Gain 1 Max HP after each combat.")

    def on_combat_end(self, player, combat):
        player.max_hp += 1


class GoldenIdol(Relic):
    def __init__(self):
        super().__init__("Golden Idol", RelicRarity.EVENT,
                         "Gain 25% more Gold.")


class GremlinVisage(Relic):
    def __init__(self):
        super().__init__("Gremlin Visage", RelicRarity.EVENT,
                         "Start each combat with 1 Weak applied to ALL enemies.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Weak
        for e in combat.enemies:
            e.effects.add(Weak(1))


class MarkOfTheBloom(Relic):
    def __init__(self):
        super().__init__("Mark of the Bloom", RelicRarity.EVENT,
                         "You can no longer heal.")


class MutagenicStrength(Relic):
    def __init__(self):
        super().__init__("Mutagenic Strength", RelicRarity.EVENT,
                         "Start each combat with 3 Strength that is lost at end of turn.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Strength
        player.effects.add(Strength(3))


class NlothsGift(Relic):
    def __init__(self):
        super().__init__("N'loth's Gift", RelicRarity.EVENT,
                         "Triple the chances of getting rare cards from normal combats.")


class NlothsMask(Relic):
    def __init__(self):
        super().__init__("N'loth's Hungry Face", RelicRarity.EVENT,
                         "The next non-boss chest is empty.")


class Necronomicon(Relic):
    def __init__(self):
        super().__init__("Necronomicon", RelicRarity.EVENT,
                         "The first Attack that costs 2+ each combat is played twice.")
        self.used_this_combat = False

    def on_combat_start(self, player, combat):
        self.used_this_combat = False


class NilrysCodex(Relic):
    def __init__(self):
        super().__init__("Nilry's Codex", RelicRarity.EVENT,
                         "At the end of your turn, you may choose 1 of 3 random cards to shuffle into your draw pile.")


class OddMushroom(Relic):
    def __init__(self):
        super().__init__("Odd Mushroom", RelicRarity.EVENT,
                         "When Vulnerable, take 25% more instead of 50% more.")


class RedMask(Relic):
    def __init__(self):
        super().__init__("Red Mask", RelicRarity.EVENT,
                         "At the start of each combat, apply 1 Weak to ALL enemies.")

    def on_combat_start(self, player, combat):
        from slay_the_spire.effect import Weak
        for e in combat.enemies:
            e.effects.add(Weak(1))


class SpiritPoop(Relic):
    def __init__(self):
        super().__init__("Spirit Poop", RelicRarity.EVENT,
                         "It's spirit poop.")


class SsserpentHead(Relic):
    def __init__(self):
        super().__init__("Ssserpent Head", RelicRarity.EVENT,
                         "Whenever you enter a ? room, gain 50 Gold.")


class WarpedTongs(Relic):
    def __init__(self):
        super().__init__("Warped Tongs", RelicRarity.EVENT,
                         "At the start of your turn, Upgrade a random card for the rest of combat.")


class GoldenEye(Relic):
    def __init__(self):
        super().__init__("Golden Eye", RelicRarity.EVENT,
                         "Whenever you Scry, Scry 2 additional cards.", color="watcher")


# ===================================================
# RELIC REGISTRY
# ===================================================

ALL_RELICS = {
    # Starters
    "burning_blood": BurningBlood, "ring_of_the_snake": RingOfTheSnake,
    "cracked_core": CrackedCore, "pure_water": PureWater,
    # Common
    "anchor": Anchor, "ancient_tea_set": AncientTeaSet, "art_of_war": ArtOfWar,
    "bag_of_marbles": BagOfMarbles, "bag_of_preparation": BagOfPreparation,
    "blood_vial": BloodVial, "bronze_scales": BronzeScales,
    "centennial_puzzle": CentennialPuzzle, "ceramic_fish": CeramicFish,
    "dream_catcher": DreamCatcher, "happy_flower": HappyFlower,
    "juzu_bracelet": JuzuBracelet, "lantern": Lantern, "maw_bank": MawBank,
    "meal_ticket": MealTicket, "nunchaku": Nunchaku,
    "oddly_smooth_stone": OddlySmoothStone, "orichalcum": Orichalcum,
    "pen_nib": PenNib, "potion_belt": PotionBelt,
    "preserved_insect": PreservedInsect, "regal_pillow": Regal_Pillow,
    "smiling_mask": SmilingMask, "strawberry": Strawberry,
    "the_boot": TheBoot, "tiny_chest": TinyChest,
    "toy_ornithopter": ToyOrnithopter, "vajra": Vajra,
    "war_paint": WarPaint, "whetstone": Whetstone,
    # Uncommon
    "blue_candle": BlueCandle, "bottled_flame": BottledFlame,
    "bottled_lightning": BottledLightning, "bottled_tornado": BottledTornado,
    "darkstone_periapt": DarkstonePeriapt, "eternal_feather": EternalFeather,
    "frozen_egg": FrozenEgg, "gremlin_horn": GremlinHorn,
    "horn_cleat": HornCleat, "ink_bottle": InkBottle, "kunai": Kunai,
    "letter_opener": LetterOpener, "matryoshka": Matryoshka,
    "meat_on_the_bone": MeatOnTheBone, "mercury_hourglass": MercuryHourglass,
    "molten_egg": MoltenEgg, "mummified_hand": MummifiedHand,
    "ornamental_fan": OrnamentalFan, "pantograph": Pantograph,
    "pear": Pear, "question_card": QuestionCard, "shuriken": Shuriken,
    "singing_bowl": SingingBowl, "strike_dummy": StrikeDummy,
    "sundial": Sundial, "symbiotic_virus": SymbioticVirus,
    "teardrop_locket": TeardropLocket, "the_courier": TheCorier,
    "toxic_egg": ToxicEgg, "white_beast_statue": WhiteBeastStatue,
    # Rare
    "bird_faced_urn": BirdFacedUrn, "calipers": Calipers,
    "captains_wheel": CaptainsWheel, "dead_branch": DeadBranch,
    "du_vu_doll": DuVuDoll, "fossilized_helix": FossilizedHelix,
    "gambling_chip": GamblingChip, "ginger": Ginger, "girya": Girya,
    "ice_cream": IceCream, "incense_burner": IncenseBurner,
    "lizard_tail": LizardTail, "mango": Mango, "old_coin": OldCoin,
    "peace_pipe": PeacePipe, "pocketwatch": Pocketwatch,
    "prayer_wheel": PrayerWheel, "shovel": Shovel,
    "stone_calendar": StoneCalendar, "thread_and_needle": ThreadAndNeedle,
    "torii": Torii, "tungsten_rod": TungstenRod,
    # Boss
    "astrolabe": Astrolabe, "black_star": BlackStar, "busted_crown": BustedCrown,
    "calling_bell": CallingBell, "coffee_dripper": CoffeeDripper,
    "cursed_key": CursedKey, "ectoplasm": Ectoplasm, "empty_cage": EmptyCage,
    "fusion_hammer": FusionHammer, "holy_water": HolyWater,
    "mark_of_pain": MarkOfPain, "pandoras_box": Pandoras_Box,
    "philosopher_stone": PhilosopherStone, "runic_cube": RunicCube,
    "runic_dome": RunicDome, "runic_pyramid": RunicPyramid,
    "sacred_bark": SacredBark, "slavers_collar": SlaversCollar,
    "snecko_eye": SneckoEye, "sozu": Sozu, "tiny_house": TinyHouse,
    "velvet_choker": VelvetChoker, "wrist_blade": WristBlade,
    # Shop
    "cauldron": Cauldron, "chemical_x": ChemicalX,
    "clockwork_souvenir": ClockworkSouvenir, "dollys_mirror": DollysMirror,
    "frozen_eye": FrozenEye, "hand_drill": HandDrill,
    "lees_waffle": LeesWaffle, "medical_kit": MedicalKit,
    "membership_card": MembershipCard, "orange_pellets": OrangePellets,
    "orrery": Orrery, "prismatic_shard": PrismaticShard,
    "sling_of_courage": SlingOfCourage, "strange_spoon": StrangeSpoon,
    "the_abacus": TheAbacus, "toolbox": Toolbox,
    # Event
    "bloody_idol": BloodyIdol, "cultist_headpiece": CultistHeadpiece,
    "enchiridion": Enchiridion, "face_of_cleric": FaceOfCleric,
    "golden_idol": GoldenIdol, "gremlin_visage": GremlinVisage,
    "mark_of_the_bloom": MarkOfTheBloom, "mutagenic_strength": MutagenicStrength,
    "nloths_gift": NlothsGift, "necronomicon": Necronomicon,
    "nilrys_codex": NilrysCodex, "odd_mushroom": OddMushroom,
    "red_mask": RedMask, "spirit_poop": SpiritPoop,
    "ssserpent_head": SsserpentHead, "warped_tongs": WarpedTongs,
    "golden_eye": GoldenEye,
}


def create_relic(relic_id):
    if relic_id in ALL_RELICS:
        return ALL_RELICS[relic_id]()
    raise ValueError(f"Unknown relic: {relic_id}")


def get_random_relic(rarity=None, exclude=None, color=None):
    """Get a random relic, optionally filtered by rarity and color."""
    import random
    exclude = exclude or set()
    candidates = []
    for rid, cls in ALL_RELICS.items():
        if rid in exclude:
            continue
        r = cls()
        if rarity and r.rarity != rarity:
            continue
        if color and r.color and r.color != color:
            continue
        if r.color and color is None:
            continue  # skip class-specific if no color filter
        candidates.append(rid)
    if not candidates:
        return None
    return create_relic(random.choice(candidates))
