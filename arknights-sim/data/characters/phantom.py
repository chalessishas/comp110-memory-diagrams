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
from core.state.unit_state import Buff
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype,
    SkillTrigger, SPGainMode, StatusKind, TICK_RATE,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.phatom import make_phatom as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
CLONE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_CLONE_TALENT_TAG = "phantom_shadow_death_burst"

# --- S2: Etude ---
_S2_TAG = "phantom_s2_etude"
_S2_ATK_RATIO = 1.00
_S2_ASPD_FLAT = 30.0
_S2_BUFF_TAG = "phantom_s2_buff"
_S2_DURATION = 20.0

_S3_TAG = "phantom_s3_the_spring"

# Talent: Infiltration — CAMOUFLAGE while S3 inactive, removed when S3 fires
_INFILTRATION_TAG = "phantom_infiltration"
_INFILTRATION_CAMO_TAG = "phantom_infiltration_camo"
_INFILTRATION_CAMO_TTL = 2.0 / TICK_RATE  # two ticks so it lapses fast when S3 fires

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


# ---------------------------------------------------------------------------
# Phantom's own talent: Infiltration (CAMOUFLAGE while S3 inactive)
# ---------------------------------------------------------------------------

def _infiltration_on_tick(world, carrier: UnitState, dt: float) -> None:
    skill_active = carrier.skill is not None and carrier.skill.active_remaining > 0.0
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _INFILTRATION_CAMO_TAG]
    if not skill_active:
        elapsed = world.global_state.elapsed
        carrier.statuses.append(StatusEffect(
            kind=StatusKind.CAMOUFLAGE,
            source_tag=_INFILTRATION_CAMO_TAG,
            expires_at=elapsed + _INFILTRATION_CAMO_TTL,
        ))


register_talent(_INFILTRATION_TAG, on_tick=_infiltration_on_tick)


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


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_FLAT, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Phantom S2 Etude — ATK+{_S2_ATK_RATIO:.0%}, ASPD+{_S2_ASPD_FLAT}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


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
    op.talents = [TalentComponent(name="Infiltration", behavior_tag=_INFILTRATION_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Etude",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
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
