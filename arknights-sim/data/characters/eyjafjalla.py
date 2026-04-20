"""Eyjafjalla (艾雅法拉) — 6* Caster (Core archetype).

Talent "Pyrobreath": While Eyjafjalla is deployed, all CASTER allies gain ATK +14%.
  Applied continuously via on_tick (covers Casters deployed after Eyjafjalla).
  Removed from all units when Eyjafjalla retreats or dies.

S2 "Volcanic Activity": ATK +160%, all attacks become AoE with radius 1.3.
  Duration 40s, sp_cost=40, initial_sp=20. Standard ARTS damage with 100% splash.
  On end: reverts ATK and splash_radius to base.

S3 "Pyroclastic Eruption": ATK +220%, AoE radius 2.0, converts attack to TRUE damage.
  Duration 50s, sp_cost=60, initial_sp=15.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.amgoat import make_amgoat as _base_stats


# --- Talent: Pyrobreath (faction-wide ATK aura for Casters) ---
_PYROBREATH_TAG = "eyjafjalla_pyrobreath"
_PYROBREATH_BUFF_TAG = "eyjafjalla_pyrobreath_atk"
_PYROBREATH_ATK_RATIO = 0.14  # +14% ATK to all Caster allies


def _pyrobreath_on_tick(world, carrier, dt: float) -> None:
    for ally in world.allies():
        if ally.profession != Profession.CASTER or ally is carrier:
            continue
        if not any(b.source_tag == _PYROBREATH_BUFF_TAG for b in ally.buffs):
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_PYROBREATH_ATK_RATIO, source_tag=_PYROBREATH_BUFF_TAG,
            ))


def _pyrobreath_cleanup(world, carrier) -> None:
    for u in world.units:
        u.buffs = [b for b in u.buffs if b.source_tag != _PYROBREATH_BUFF_TAG]


register_talent(
    _PYROBREATH_TAG,
    on_tick=_pyrobreath_on_tick,
    on_retreat=_pyrobreath_cleanup,
    on_death=_pyrobreath_cleanup,
)


CORE_CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

# --- S2: Volcanic Activity ---
_S2_TAG = "eyjafjalla_s2_volcanic_activity"
_S2_ATK_RATIO = 1.60
_S2_SPLASH_RADIUS = 1.3
_S2_BUFF_TAG = "eyjafjalla_s2_atk_buff"


def _s2_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    unit._saved_splash_radius = unit.splash_radius
    unit.splash_radius = _S2_SPLASH_RADIUS


def _s2_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S2_BUFF_TAG]
    unit.splash_radius = getattr(unit, "_saved_splash_radius", 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Pyroclastic Eruption ---
_S3_TAG = "eyjafjalla_s3_pyroclastic"
_S3_ATK_RATIO = 2.20
_S3_SPLASH_RADIUS = 2.0
_S3_BUFF_TAG = "eyjafjalla_s3_atk_buff"


def _s3_on_start(world, unit) -> None:
    unit.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    unit._saved_splash_radius = unit.splash_radius
    unit._saved_attack_type = unit.attack_type
    unit.splash_radius = _S3_SPLASH_RADIUS
    unit.attack_type = AttackType.TRUE


def _s3_on_end(world, unit) -> None:
    unit.buffs = [b for b in unit.buffs if b.source_tag != _S3_BUFF_TAG]
    unit.splash_radius = getattr(unit, "_saved_splash_radius", 0.0)
    unit.attack_type = getattr(unit, "_saved_attack_type", AttackType.ARTS)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_eyjafjalla(slot: str = "S2") -> UnitState:
    """Eyjafjalla E2 max. Talent: Pyrobreath +14% ATK aura to all Casters. S2/S3 skills."""
    op = _base_stats()
    op.name = "Eyjafjalla"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.range_shape = CORE_CASTER_RANGE
    op.block = 1
    op.cost = 21

    op.talents = [TalentComponent(name="Pyrobreath", behavior_tag=_PYROBREATH_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Volcanic Activity",
            slot="S2",
            sp_cost=40,
            initial_sp=20,
            duration=40.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Pyroclastic Eruption",
            slot="S3",
            sp_cost=60,
            initial_sp=15,
            duration=50.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
