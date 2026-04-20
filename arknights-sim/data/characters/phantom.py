"""Phantom (傀影) — 6★ Specialist (Executor archetype).

S3 "The Spring": Deploys a Shadow clone at Phantom's position for _CLONE_DURATION seconds.
  The clone fights autonomously (physical, melee). When the clone dies (or S3 ends),
  it releases a burst of Arts damage to all enemies within Chebyshev distance 1
  (the 8 surrounding tiles).

Base stats from ArknightsGameData (E2 max, trust 100, char_250_phatom):
  HP=1645, ATK=648, DEF=322, RES=0, atk_interval=0.93, block=1, SPECIALIST.

Shadow clone stats (approximate, matches Phantom's ATK at S3 rank VII):
  HP=3000, ATK=648, DEF=100, RES=0, atk_interval=0.93, block=2, PHYSICAL.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
    SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.phatom import make_phatom as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
CLONE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_CLONE_TALENT_TAG = "phantom_shadow_death_burst"
_S3_TAG = "phantom_s3_the_spring"

_CLONE_HP = 3000
_CLONE_ATK = 648     # mirrors Phantom's ATK
_CLONE_DURATION = 30.0
_BURST_ARTS_DAMAGE = 500  # Arts damage on clone death (approximate rank VII)


# ---------------------------------------------------------------------------
# Shadow clone talent — Arts burst on death
# ---------------------------------------------------------------------------

def _clone_burst_on_death(world, unit: UnitState) -> None:
    """Shadow clone dies → Arts damage to all enemies in Chebyshev-1."""
    if unit.position is None:
        return
    cx, cy = unit.position
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        if max(abs(round(ex) - round(cx)), abs(round(ey) - round(cy))) <= 1:
            dmg = e.take_arts(_BURST_ARTS_DAMAGE)
            world.global_state.total_damage_dealt += dmg
            world.log(
                f"Phantom Shadow burst → {e.name}  "
                f"arts_dmg={dmg}  ({e.hp}/{e.max_hp})"
            )


register_talent(_CLONE_TALENT_TAG, on_death=_clone_burst_on_death)


def _make_shadow_clone(position: tuple[float, float]) -> UnitState:
    """Phantom's shadow clone — physical melee, carries death-burst talent."""
    clone = UnitState(
        name="Shadow",
        faction=Faction.ALLY,
        max_hp=_CLONE_HP,
        hp=_CLONE_HP,
        atk=_CLONE_ATK,
        defence=100,
        res=0.0,
        atk_interval=0.93,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        range_shape=CLONE_RANGE,
        block=2,
        cost=0,
        deployed=True,
        position=position,
    )
    clone.talents = [TalentComponent(name="Shadow Burst", behavior_tag=_CLONE_TALENT_TAG)]
    return clone


# ---------------------------------------------------------------------------
# S3: The Spring — deploy shadow clone
# ---------------------------------------------------------------------------

def _s3_on_start(world, carrier: UnitState) -> None:
    pos = carrier.position if carrier.position is not None else (0.0, 0.0)
    clone = _make_shadow_clone(pos)
    world.add_unit(clone)
    carrier._phantom_clone_id = clone.unit_id
    world.log(f"Phantom S3: Shadow deployed  HP={clone.hp}  pos={pos}")


def _s3_on_end(world, carrier: UnitState) -> None:
    clone_id = getattr(carrier, "_phantom_clone_id", None)
    if clone_id is not None:
        clone = world.unit_by_id(clone_id)
        if clone is not None and clone.alive:
            # S3 ends naturally → trigger the burst via on_death
            clone.hp = 0
            clone.alive = False
            clone._just_died = True
    carrier._phantom_clone_id = None


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def make_phantom(slot: str = "S3") -> UnitState:
    """Phantom E2 max, trust 100. S3 deploys Shadow clone with Arts death burst."""
    op = _base_stats()
    op.name = "Phantom"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = EXECUTOR_RANGE
    op.block = 1
    op.cost = 10

    if slot == "S3":
        op.skill = SkillComponent(
            name="The Spring",
            slot="S3",
            sp_cost=35,
            initial_sp=15,
            duration=_CLONE_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
