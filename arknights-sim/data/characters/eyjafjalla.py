"""Eyjafjalla (艾雅法拉) — 6* Caster (Core archetype).

S2 "Volcanic Activity": ATK +160%, all attacks become AoE with radius 1.3.
  Duration 40s, sp_cost=40, initial_sp=20. Standard ARTS damage with 100% splash.
  On end: reverts ATK and splash_radius to base.

S3 "Pyroclastic Eruption": ATK +220%, AoE radius 2.0, converts attack to TRUE damage.
  Duration 50s, sp_cost=60, initial_sp=15.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from data.characters.generated.amgoat import make_amgoat as _base_stats


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
    """Eyjafjalla E2 max. S2: +160% ATK + AoE r=1.3. S3: +220% ATK + AoE r=2.0 TRUE."""
    op = _base_stats()
    op.name = "Eyjafjalla"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.range_shape = CORE_CASTER_RANGE
    op.block = 1
    op.cost = 21

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
