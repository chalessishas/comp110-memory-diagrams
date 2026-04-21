"""Deepcolor (深海色) — 4★ Supporter (SUP_SUMMONER archetype) + Jellyfish summons.

Talent "Aquatic Life":
  When a Jellyfish (Generation 1) dies in combat, a smaller Jellyfish (Generation 2)
  is spawned at the same position. Generation 2 does not re-spawn on death.

S2 "Tentacle Feast": Deploys a Jellyfish (G1) at Deepcolor's position for 30s.
  When S2 ends or Deepcolor retreats/dies, all active Jellyfish are silently despawned
  (no combat death → no G2 respawn triggered).

Base stats from ArknightsGameData (E2 max, trust 100, char_110_deepcl):
  HP=1350, ATK=403, DEF=125, RES=15%, atk_interval=1.6, block=1, SUPPORTER.

Jellyfish stats (approximate):
  G1: HP=800, ATK=403, DEF=0, block=0, Arts, atk_interval=2.0
  G2: HP=400, ATK=201, DEF=0, block=0, Arts, atk_interval=2.0
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.deepcl import make_deepcl as _base_stats


DEEPCOLOR_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(1, 4) for dy in range(-1, 2)
))
JELLYFISH_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_JELLY_G1_TALENT_TAG = "deepcolor_jelly_g1_respawn"
_DEEPCOLOR_TALENT_TAG = "deepcolor_aquatic_life_carrier"
_S2_TAG = "deepcolor_s2_tentacle_feast"

_JELLY_G1_HP = 800
_JELLY_G1_ATK = 403
_JELLY_G2_HP = 400
_JELLY_G2_ATK = 201


# ---------------------------------------------------------------------------
# Jellyfish units
# ---------------------------------------------------------------------------

def _make_jellyfish(position: tuple[float, float], generation: int = 1) -> UnitState:
    """Jellyfish summon. G1 carries the re-spawn talent; G2 does not."""
    hp = _JELLY_G1_HP if generation == 1 else _JELLY_G2_HP
    atk = _JELLY_G1_ATK if generation == 1 else _JELLY_G2_ATK
    jelly = UnitState(
        name=f"Jellyfish-G{generation}",
        faction=Faction.ALLY,
        max_hp=hp,
        hp=hp,
        atk=atk,
        defence=0,
        res=0.0,
        atk_interval=2.0,
        attack_type=AttackType.ARTS,
        attack_range_melee=True,
        range_shape=JELLYFISH_RANGE,
        block=0,
        cost=0,
        deployed=True,
        position=position,
    )
    if generation == 1:
        jelly.talents = [TalentComponent(name="Aquatic Life", behavior_tag=_JELLY_G1_TALENT_TAG)]
    return jelly


def _jelly_g1_on_death(world, unit: UnitState) -> None:
    """G1 Jellyfish dies in combat → spawn G2 at same position."""
    if unit.position is None:
        return
    g2 = _make_jellyfish(unit.position, generation=2)
    world.add_unit(g2)
    # Register G2 ID back on Deepcolor so S2 on_end can despawn it
    carrier_id = getattr(unit, "_dc_carrier_id", None)
    if carrier_id is not None:
        carrier = world.unit_by_id(carrier_id)
        if carrier is not None:
            carrier._dc_jelly_g2_id = g2.unit_id
    world.log(f"Deepcolor: Jellyfish G1 died → G2 spawned  pos={unit.position}")


register_talent(_JELLY_G1_TALENT_TAG, on_death=_jelly_g1_on_death)


# ---------------------------------------------------------------------------
# Deepcolor carrier talent — lifecycle management
# ---------------------------------------------------------------------------

def _despawn_jellies(world, carrier: UnitState) -> None:
    """Silently remove G1 and G2 (no _just_died → no on_death cascade)."""
    g1_id = getattr(carrier, "_dc_jelly_id", None)
    if g1_id is not None:
        g1 = world.unit_by_id(g1_id)
        if g1 is not None and g1.alive:
            g1.alive = False
            g1.hp = 0
            g1.deployed = False
    carrier._dc_jelly_id = None

    g2_id = getattr(carrier, "_dc_jelly_g2_id", None)
    if g2_id is not None:
        g2 = world.unit_by_id(g2_id)
        if g2 is not None and g2.alive:
            g2.alive = False
            g2.hp = 0
            g2.deployed = False
    carrier._dc_jelly_g2_id = None


register_talent(
    _DEEPCOLOR_TALENT_TAG,
    on_death=_despawn_jellies,
    on_retreat=_despawn_jellies,
)


# ---------------------------------------------------------------------------
# S2: Tentacle Feast — deploy Jellyfish G1
# ---------------------------------------------------------------------------

def _s2_on_start(world, carrier: UnitState) -> None:
    pos = carrier.position if carrier.position is not None else (0.0, 0.0)
    g1 = _make_jellyfish(pos, generation=1)
    g1._dc_carrier_id = carrier.unit_id
    world.add_unit(g1)
    carrier._dc_jelly_id = g1.unit_id
    carrier._dc_jelly_g2_id = None
    world.log(f"Deepcolor S2: Jellyfish-G1 deployed  HP={g1.hp}  pos={pos}")


def _s2_on_end(world, carrier: UnitState) -> None:
    _despawn_jellies(world, carrier)


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# ---------------------------------------------------------------------------
# S3: Abyssal Tide — deploy 2 Jellyfish G1
# ---------------------------------------------------------------------------

_S3_TAG = "deepcolor_s3_abyssal_tide"
_DC_S3_JELLY_ATTR = "_dc_s3_jelly_ids"


def _s3_on_start(world, carrier: UnitState) -> None:
    pos = carrier.position if carrier.position is not None else (0.0, 0.0)
    ids = []
    for _ in range(2):
        g1 = _make_jellyfish(pos, generation=1)
        g1._dc_carrier_id = carrier.unit_id
        world.add_unit(g1)
        ids.append(g1.unit_id)
    setattr(carrier, _DC_S3_JELLY_ATTR, ids)
    world.log(f"Deepcolor S3: 2× Jellyfish-G1 deployed  pos={pos}")


def _s3_on_end(world, carrier: UnitState) -> None:
    for jid in getattr(carrier, _DC_S3_JELLY_ATTR, []):
        u = world.unit_by_id(jid)
        if u is not None and u.alive:
            u.alive = False
            u.hp = 0
            u.deployed = False
    setattr(carrier, _DC_S3_JELLY_ATTR, [])


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_deepcolor(slot: str = "S2") -> UnitState:
    """Deepcolor E2 max, trust 100. S2 deploys 1 Jellyfish G1. S3 deploys 2 Jellyfish G1."""
    op = _base_stats()
    op.name = "Deepcolor"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = DEEPCOLOR_RANGE
    op.block = 1
    op.cost = 10

    op.talents = [TalentComponent(name="Aquatic Life", behavior_tag=_DEEPCOLOR_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Tentacle Feast",
            slot="S2",
            sp_cost=28,
            initial_sp=0,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Abyssal Tide",
            slot="S3",
            sp_cost=35,
            initial_sp=10,
            duration=35.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
