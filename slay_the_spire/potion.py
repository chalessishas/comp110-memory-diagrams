"""Potion system for Slay the Spire."""
from enum import Enum, auto


class PotionRarity(Enum):
    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()


class PotionColor(Enum):
    ANY = auto()
    RED = auto()
    GREEN = auto()
    BLUE = auto()
    PURPLE = auto()


class Potion:
    """Base class for potions."""

    def __init__(self, name, rarity, color=PotionColor.ANY, description="",
                 requires_target=False):
        self.name = name
        self.rarity = rarity
        self.color = color
        self.description = description
        self.requires_target = requires_target

    def use(self, player, combat=None, target=None):
        """Override in subclass."""
        pass

    def __repr__(self):
        return self.name


# === All Potions ===

class BloodPotion(Potion):
    def __init__(self):
        super().__init__("Blood Potion", PotionRarity.COMMON, PotionColor.RED,
                         "Heal for 20% of your Max HP.")

    def use(self, player, combat=None, target=None):
        player.heal(int(player.max_hp * 0.2))


class ElixirPotion(Potion):
    def __init__(self):
        super().__init__("Elixir", PotionRarity.UNCOMMON, PotionColor.RED,
                         "Exhaust any number of cards in your hand.")

    def use(self, player, combat=None, target=None):
        # Interactive: handled in combat UI
        pass


class HeartOfIron(Potion):
    def __init__(self):
        super().__init__("Heart of Iron", PotionRarity.RARE, PotionColor.RED,
                         "Gain 6 Metallicize.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Metallicize
        player.effects.add(Metallicize(6))


class PoisonPotion(Potion):
    def __init__(self):
        super().__init__("Poison Potion", PotionRarity.COMMON, PotionColor.GREEN,
                         "Apply 6 Poison to a target enemy.", requires_target=True)

    def use(self, player, combat=None, target=None):
        if target:
            from slay_the_spire.effect import Poison
            target.effects.add(Poison(6))


class CunningPotion(Potion):
    def __init__(self):
        super().__init__("Cunning Potion", PotionRarity.UNCOMMON, PotionColor.GREEN,
                         "Add 3 Shivs to your hand.")

    def use(self, player, combat=None, target=None):
        if combat:
            from slay_the_spire.card import create_card
            for _ in range(3):
                try:
                    shiv = create_card("shiv")
                    player.hand.append(shiv)
                except:
                    pass


class GhostInAJar(Potion):
    def __init__(self):
        super().__init__("Ghost In A Jar", PotionRarity.RARE, PotionColor.GREEN,
                         "Gain 1 Intangible.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Intangible
        player.effects.add(Intangible(1))


class FocusPotion(Potion):
    def __init__(self):
        super().__init__("Focus Potion", PotionRarity.COMMON, PotionColor.BLUE,
                         "Gain 2 Focus.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Focus
        player.effects.add(Focus(2))


class PotionOfCapacity(Potion):
    def __init__(self):
        super().__init__("Potion of Capacity", PotionRarity.UNCOMMON, PotionColor.BLUE,
                         "Gain 2 Orb slots.")

    def use(self, player, combat=None, target=None):
        player.orbs.increase_max(2)


class EssenceOfDarkness(Potion):
    def __init__(self):
        super().__init__("Essence of Darkness", PotionRarity.RARE, PotionColor.BLUE,
                         "Channel 1 Dark for each Orb slot.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.orb import OrbType
        for _ in range(player.orbs.max_orbs):
            player.orbs.channel(OrbType.DARK)


class BottledMiracle(Potion):
    def __init__(self):
        super().__init__("Bottled Miracle", PotionRarity.COMMON, PotionColor.PURPLE,
                         "Add 2 Miracles to your hand.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.card import create_card
        for _ in range(2):
            try:
                m = create_card("miracle")
                player.hand.append(m)
            except:
                pass


class StancePotion(Potion):
    def __init__(self):
        super().__init__("Stance Potion", PotionRarity.UNCOMMON, PotionColor.PURPLE,
                         "Enter Wrath or Calm.")

    def use(self, player, combat=None, target=None):
        # Interactive: handled in UI
        pass


class Ambrosia(Potion):
    def __init__(self):
        super().__init__("Ambrosia", PotionRarity.RARE, PotionColor.PURPLE,
                         "Enter Divinity.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.stance import StanceType
        player.stance.enter(StanceType.DIVINITY)


# === Colorless Potions ===

class EnergyPotion(Potion):
    def __init__(self):
        super().__init__("Energy Potion", PotionRarity.COMMON,
                         description="Gain 2 Energy.")

    def use(self, player, combat=None, target=None):
        player.gain_energy(2)


class FirePotion(Potion):
    def __init__(self):
        super().__init__("Fire Potion", PotionRarity.COMMON,
                         description="Deal 20 damage to target enemy.", requires_target=True)

    def use(self, player, combat=None, target=None):
        if target and combat:
            combat.deal_damage_to_enemy(target, 20)


class ExplosivePotion(Potion):
    def __init__(self):
        super().__init__("Explosive Potion", PotionRarity.COMMON,
                         description="Deal 10 damage to ALL enemies.")

    def use(self, player, combat=None, target=None):
        if combat:
            for e in combat.enemies:
                if e.is_alive:
                    combat.deal_damage_to_enemy(e, 10)


class BlockPotion(Potion):
    def __init__(self):
        super().__init__("Block Potion", PotionRarity.COMMON,
                         description="Gain 12 Block.")

    def use(self, player, combat=None, target=None):
        player.gain_block_raw(12)


class DexterityPotion(Potion):
    def __init__(self):
        super().__init__("Dexterity Potion", PotionRarity.COMMON,
                         description="Gain 2 Dexterity.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Dexterity
        player.effects.add(Dexterity(2))


class StrengthPotion(Potion):
    def __init__(self):
        super().__init__("Strength Potion", PotionRarity.COMMON,
                         description="Gain 2 Strength.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Strength
        player.effects.add(Strength(2))


class SwiftPotion(Potion):
    def __init__(self):
        super().__init__("Swift Potion", PotionRarity.COMMON,
                         description="Draw 3 cards.")

    def use(self, player, combat=None, target=None):
        player.draw_cards(3)


class WeakPotion(Potion):
    def __init__(self):
        super().__init__("Weak Potion", PotionRarity.COMMON,
                         description="Apply 3 Weak to target enemy.", requires_target=True)

    def use(self, player, combat=None, target=None):
        if target:
            from slay_the_spire.effect import Weak
            target.effects.add(Weak(3))


class FearPotion(Potion):
    def __init__(self):
        super().__init__("Fear Potion", PotionRarity.COMMON,
                         description="Apply 3 Vulnerable to target enemy.", requires_target=True)

    def use(self, player, combat=None, target=None):
        if target:
            from slay_the_spire.effect import Vulnerable
            target.effects.add(Vulnerable(3))


class AttackPotion(Potion):
    def __init__(self):
        super().__init__("Attack Potion", PotionRarity.COMMON,
                         description="Add 1 random Attack to your hand (upgraded, costs 0 this turn).")

    def use(self, player, combat=None, target=None):
        pass  # Complex: generate random attack card


class SkillPotion(Potion):
    def __init__(self):
        super().__init__("Skill Potion", PotionRarity.COMMON,
                         description="Add 1 random Skill to your hand (upgraded, costs 0 this turn).")

    def use(self, player, combat=None, target=None):
        pass


class PowerPotion(Potion):
    def __init__(self):
        super().__init__("Power Potion", PotionRarity.COMMON,
                         description="Add 1 random Power to your hand (upgraded, costs 0 this turn).")

    def use(self, player, combat=None, target=None):
        pass


class ColorlessPotion(Potion):
    def __init__(self):
        super().__init__("Colorless Potion", PotionRarity.COMMON,
                         description="Add 1 random Colorless card to your hand (upgraded, costs 0 this turn).")

    def use(self, player, combat=None, target=None):
        pass


class RegenPotion(Potion):
    def __init__(self):
        super().__init__("Regen Potion", PotionRarity.UNCOMMON,
                         description="Gain 5 Regeneration.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Regeneration
        player.effects.add(Regeneration(5))


class AncientPotion(Potion):
    def __init__(self):
        super().__init__("Ancient Potion", PotionRarity.UNCOMMON,
                         description="Gain 1 Artifact.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Artifact
        player.effects.add(Artifact(1))


class DistilledChaos(Potion):
    def __init__(self):
        super().__init__("Distilled Chaos", PotionRarity.UNCOMMON,
                         description="Play the top 3 cards of your draw pile.")

    def use(self, player, combat=None, target=None):
        pass  # Complex: handled in combat


class DuplicationPotion(Potion):
    def __init__(self):
        super().__init__("Duplication Potion", PotionRarity.UNCOMMON,
                         description="This turn, your next card is played twice.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Double_Tap
        player.effects.add(Double_Tap(1))


class EssenceOfSteel(Potion):
    def __init__(self):
        super().__init__("Essence of Steel", PotionRarity.UNCOMMON,
                         description="Gain 4 Plated Armor.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Plated_Armor
        player.effects.add(Plated_Armor(4))


class GamblersBrew(Potion):
    def __init__(self):
        super().__init__("Gambler's Brew", PotionRarity.UNCOMMON,
                         description="Discard any number of cards, then draw that many.")

    def use(self, player, combat=None, target=None):
        pass  # Interactive: handled in UI


class LiquidBronze(Potion):
    def __init__(self):
        super().__init__("Liquid Bronze", PotionRarity.UNCOMMON,
                         description="Gain 3 Thorns.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Thorns
        player.effects.add(Thorns(3))


class LiquidMemories(Potion):
    def __init__(self):
        super().__init__("Liquid Memories", PotionRarity.UNCOMMON,
                         description="Choose a card in your discard pile and return it to your hand. It costs 0 this turn.")

    def use(self, player, combat=None, target=None):
        pass  # Interactive


class SmokeBomb(Potion):
    def __init__(self):
        super().__init__("Smoke Bomb", PotionRarity.UNCOMMON,
                         description="Escape from a non-boss combat.")

    def use(self, player, combat=None, target=None):
        if combat and not combat.is_boss:
            combat.escaped = True


class SneckoOil(Potion):
    def __init__(self):
        super().__init__("Snecko Oil", PotionRarity.RARE,
                         description="Draw 5 cards. Randomize their costs.")

    def use(self, player, combat=None, target=None):
        import random
        drawn = player.draw_cards(5)
        for c in drawn:
            c.cost_for_turn = random.randint(0, 3)


class FairyInABottle(Potion):
    def __init__(self):
        super().__init__("Fairy in a Bottle", PotionRarity.RARE,
                         description="When you would die, heal to 30% of your Max HP instead.")

    def use(self, player, combat=None, target=None):
        # Passive: triggered on death
        player.heal(int(player.max_hp * 0.3))


class FruitJuice(Potion):
    def __init__(self):
        super().__init__("Fruit Juice", PotionRarity.RARE,
                         description="Gain 5 Max HP.")

    def use(self, player, combat=None, target=None):
        player.max_hp += 5
        player.hp += 5


class EntropicBrew(Potion):
    def __init__(self):
        super().__init__("Entropic Brew", PotionRarity.RARE,
                         description="Fill all your potion slots with random potions.")

    def use(self, player, combat=None, target=None):
        import random
        for i in range(player.max_potions):
            if player.potions[i] is None:
                player.potions[i] = get_random_potion()


class CultistPotion(Potion):
    def __init__(self):
        super().__init__("Cultist Potion", PotionRarity.RARE,
                         description="Gain 1 Ritual.")

    def use(self, player, combat=None, target=None):
        from slay_the_spire.effect import Ritual
        player.effects.add(Ritual(1))


# === Potion Registry ===

ALL_POTIONS = {
    # Colorless
    "energy_potion": EnergyPotion,
    "fire_potion": FirePotion,
    "explosive_potion": ExplosivePotion,
    "block_potion": BlockPotion,
    "dexterity_potion": DexterityPotion,
    "strength_potion": StrengthPotion,
    "swift_potion": SwiftPotion,
    "weak_potion": WeakPotion,
    "fear_potion": FearPotion,
    "attack_potion": AttackPotion,
    "skill_potion": SkillPotion,
    "power_potion": PowerPotion,
    "colorless_potion": ColorlessPotion,
    "regen_potion": RegenPotion,
    "ancient_potion": AncientPotion,
    "distilled_chaos": DistilledChaos,
    "duplication_potion": DuplicationPotion,
    "essence_of_steel": EssenceOfSteel,
    "gamblers_brew": GamblersBrew,
    "liquid_bronze": LiquidBronze,
    "liquid_memories": LiquidMemories,
    "smoke_bomb": SmokeBomb,
    "snecko_oil": SneckoOil,
    "fairy_in_a_bottle": FairyInABottle,
    "fruit_juice": FruitJuice,
    "entropic_brew": EntropicBrew,
    "cultist_potion": CultistPotion,
    # Red
    "blood_potion": BloodPotion,
    "elixir": ElixirPotion,
    "heart_of_iron": HeartOfIron,
    # Green
    "poison_potion": PoisonPotion,
    "cunning_potion": CunningPotion,
    "ghost_in_a_jar": GhostInAJar,
    # Blue
    "focus_potion": FocusPotion,
    "potion_of_capacity": PotionOfCapacity,
    "essence_of_darkness": EssenceOfDarkness,
    # Purple
    "bottled_miracle": BottledMiracle,
    "stance_potion": StancePotion,
    "ambrosia": Ambrosia,
}

COMMON_POTIONS = [k for k, v in ALL_POTIONS.items() if v().rarity == PotionRarity.COMMON]
UNCOMMON_POTIONS = [k for k, v in ALL_POTIONS.items() if v().rarity == PotionRarity.UNCOMMON]
RARE_POTIONS = [k for k, v in ALL_POTIONS.items() if v().rarity == PotionRarity.RARE]


def create_potion(potion_id):
    if potion_id in ALL_POTIONS:
        return ALL_POTIONS[potion_id]()
    raise ValueError(f"Unknown potion: {potion_id}")


def get_random_potion(character_class=None):
    """Get a random potion, weighted by rarity."""
    import random
    roll = random.random()
    if roll < 0.65:
        pool = COMMON_POTIONS
    elif roll < 0.90:
        pool = UNCOMMON_POTIONS
    else:
        pool = RARE_POTIONS
    pid = random.choice(pool)
    return create_potion(pid)
