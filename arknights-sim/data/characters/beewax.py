"""蜜蜡 (Beewax) — 5★ Caster (Mystic Caster).

S1 "沙暴扩散": sp_cost=18, initial_sp=8, duration=20s, MANUAL, AUTO_TIME.
  ATK +60%.

S2 "沙暴聚焦": sp_cost=30, initial_sp=10, duration=20s, MANUAL, AUTO_TIME.
  ATK×300% + STUN 3s enemies in range (not yet modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.beewax import make_beewax as _base_stats

CASTER_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1), (2, -1), (2, 1)))

# --- S1 ---
_S1_TAG = "beewax_s1_sandstorm_spread"
_S1_ATK_RATIO = 0.60
_S1_BUFF_TAG = "beewax_s1_atk"
_S1_DURATION = 20.0

# --- S2 ---
_S2_TAG = "beewax_s2_sandstorm_focus"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Beewax S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_beewax(slot: str = "S1") -> UnitState:
    """Beewax E2 max. S1: ATK+60%/20s. S2: ATK×300%+STUN (not modeled)."""
    op = _base_stats()
    op.name = "Beewax"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Sandstorm Spread",
            slot="S1",
            sp_cost=18,
            initial_sp=8,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Sandstorm Focus",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
