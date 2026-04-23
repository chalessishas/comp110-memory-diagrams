"""Blue Poison (蓝毒) — 4★ Sniper (Deadeye).

S1 "Twinshot - Auto": sp_cost=2, initial_sp=0, duration=-1 (auto-trigger, stub).

S2 "Venom Spray": sp_cost=40, initial_sp=25, duration=30s, MANUAL, AUTO_TIME.
  ATK +50% (multi-target not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.bluep import make_bluep as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "bluep_s1_twinshot"
_S1_DURATION = 0.0

_S2_TAG = "bluep_s2_venom_spray"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "bluep_s2_atk"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"BluP S2 — ATK+{_S2_ATK_RATIO*100:.0f}%/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_bluep(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "BluP"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Twinshot - Auto", slot="S1", sp_cost=2, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Venom Spray", slot="S2", sp_cost=40, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
