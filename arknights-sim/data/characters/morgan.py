"""Morgan (摩根) — 5★ Guard (Dreadnought).

S1 "Professional Street Fighter": sp_cost=24, initial_sp=6, duration=12s, AUTO_TIME, MANUAL.
  ATK +60%. HP drain 12% current HP per attack not modeled.
S2 "Dauntless Resistance": sp_cost=0, initial_sp=0, ON_DEPLOY, AUTO.
  Loses 70% MaxHP, gains decaying barrier, ATK+60%. Complex barrier mechanic — stub only.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.morgan import make_morgan as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- S1 ---
_S1_TAG = "morgan_s1_street_fighter"
_S1_ATK_RATIO = 0.60
_S1_BUFF_TAG = "morgan_s1_atk"
_S1_DURATION = 12.0

# --- S2 ---
_S2_TAG = "morgan_s2"; _S2_DURATION = 18.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Morgan S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (HP drain not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_morgan(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Morgan"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Professional Street Fighter", slot="S1", sp_cost=24, initial_sp=6,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Dauntless Resistance", slot="S2", sp_cost=0, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
