"""Ling (令) — 6★ Supporter (Summoner archetype).

SUP_SUMMONER trait: Can summon Long Xian dragons to fight alongside the operator.
  The summoned unit is a full UnitState (faction=ALLY) added to the world via
  world.add_unit(). Long Xian persists until S3 ends, at which point it is
  recalled (alive set to False).

Talent "Dragon's Blood": While a Long Xian is deployed, all allies in Ling's
  range gain +_TALENT_ATK_BONUS flat ATK. Applied via on_tick aura (same
  pattern as Pallas's inspiration, but conditional on summon presence).

S3 "Draconic Inspiration": 30s duration. Summon a Long Xian at Ling's position.
  Long Xian fights autonomously (physical, melee, block=2). On S3 end, the Long
  Xian is recalled.
  sp_cost=55, initial_sp=25, AUTO_TIME, AUTO trigger, requires_target=False.

Base stats from ArknightsGameData (E2 max, trust 100, char_2023_ling):
  HP=1429, ATK=508, DEF=138, RES=20, atk_interval=1.6, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ling import make_ling as _base_stats


SUMMONER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))
LONG_XIAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# Talent: Dragon's Blood — ATK aura to allies while Long Xian is deployed
_TALENT_TAG = "ling_dragons_blood"
_TALENT_ATK_BONUS = 60          # +60 flat ATK to allies in range
_TALENT_BUFF_TAG = "ling_dragon_atk"
_TALENT_BUFF_TTL = 0.3          # seconds; re-stamped each tick

# S3: Draconic Inspiration
_S3_TAG = "ling_s3_draconic_inspiration"
_S3_DURATION = 30.0
_LONG_XIAN_ATK = 900
_LONG_XIAN_HP = 4000
_LONG_XIAN_DEF = 200


def _has_summon(world, carrier: UnitState) -> bool:
    summon_id = getattr(carrier, "_ling_summon_id", None)
    if summon_id is None:
        return False
    unit = world.unit_by_id(summon_id)
    return unit is not None and unit.alive


def _in_summoner_range(carrier: UnitState, ally: UnitState) -> bool:
    if carrier.position is None or ally.position is None:
        return False
    cx, cy = carrier.position
    alx, aly = ally.position
    return any(
        (cx + dx == alx and cy + dy == aly)
        for dx, dy in SUMMONER_RANGE.tiles
    )


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    now = world.global_state.elapsed
    new_expires = now + _TALENT_BUFF_TTL + dt
    summon_present = _has_summon(world, carrier)

    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not summon_present or not _in_summoner_range(carrier, ally):
            ally.buffs = [b for b in ally.buffs if b.source_tag != _TALENT_BUFF_TAG]
            continue
        existing = next((b for b in ally.buffs if b.source_tag == _TALENT_BUFF_TAG), None)
        if existing is not None:
            existing.expires_at = new_expires
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.FLAT,
                value=_TALENT_ATK_BONUS, source_tag=_TALENT_BUFF_TAG,
                expires_at=new_expires,
            ))


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _make_long_xian(position: tuple[float, float]) -> UnitState:
    """Long Xian dragon — summoned ally unit. Physical melee, block=2."""
    return UnitState(
        name="Long Xian",
        faction=Faction.ALLY,
        max_hp=_LONG_XIAN_HP,
        hp=_LONG_XIAN_HP,
        atk=_LONG_XIAN_ATK,
        defence=_LONG_XIAN_DEF,
        res=0.0,
        atk_interval=2.0,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=LONG_XIAN_RANGE,
        block=2,
        cost=0,
        deployed=True,
        position=position,
    )


def _s3_on_start(world, carrier: UnitState) -> None:
    pos = carrier.position if carrier.position is not None else (0.0, 0.0)
    dragon = _make_long_xian(pos)
    world.add_unit(dragon)
    carrier._ling_summon_id = dragon.unit_id
    world.log(
        f"Ling S3: Long Xian deployed  "
        f"HP={dragon.hp}  ATK={dragon.atk}  pos={pos}"
    )


def _s3_on_end(world, carrier: UnitState) -> None:
    summon_id = getattr(carrier, "_ling_summon_id", None)
    if summon_id is not None:
        unit = world.unit_by_id(summon_id)
        if unit is not None and unit.alive:
            unit.alive = False
            unit.hp = 0
            world.log(f"Ling S3 ended: Long Xian recalled")
    carrier._ling_summon_id = None


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_ling(slot: str = "S3") -> UnitState:
    """Ling E2 max. SUP_SUMMONER: summons Long Xian dragon during S3; ally ATK aura while dragon lives."""
    op = _base_stats()
    op.name = "Ling"
    op.archetype = RoleArchetype.SUP_SUMMONER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = SUMMONER_RANGE
    op.block = 1
    op.cost = 12

    op.talents = [TalentComponent(name="Dragon's Blood", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Draconic Inspiration",
            slot="S3",
            sp_cost=55,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
