"""Poncirus (柚子) — 4★ Vanguard (Pioneer).

S1 "Charge γ" (shared skcom_charge_cost[3]):
  sp_cost=35, initial_sp=20, duration=0s (instant DP, stub).

S2 "Engineer's Wish": sp_cost=40, initial_sp=25, duration=15s, MANUAL, AUTO_TIME.
  ATK +35%, DEF +65%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.buildr import make_buildr as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "buildr_s1_charge"
_S1_DURATION = 0.0

_S2_TAG = "buildr_s2_engineers_wish"
_S2_ATK_RATIO = 0.35
_S2_DEF_RATIO = 0.65
_S2_ATK_BUFF_TAG = "buildr_s2_atk"
_S2_DEF_BUFF_TAG = "buildr_s2_def"
_S2_DURATION = 15.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG))
    world.log(f"Buildr S2 — ATK+{_S2_ATK_RATIO*100:.0f}% DEF+{_S2_DEF_RATIO*100:.0f}%/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_buildr(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Buildr"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Charge γ", slot="S1", sp_cost=35, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Engineer's Wish", slot="S2", sp_cost=40, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
