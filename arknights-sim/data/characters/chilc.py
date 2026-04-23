"""Chilchuck (齐尔查克) — 5★ Limited Vanguard (Agent). Delicious in Dungeon collab.

S1 "Lockpicks": sp_cost=12, initial_sp=9, 3s (random DP 3-9, stub).

S2 "Improvisation": sp_cost=25, initial_sp=14, duration=10s, MANUAL, OFFENSIVE.
  ASPD +50 (dodge+DP-per-attack not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.chilc import make_chilc as _base_stats

PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "chilc_s1_lockpicks"
_S1_DURATION = 3.0

_S2_TAG = "chilc_s2_improvisation"
_S2_ASPD_FLAT = 50.0
_S2_BUFF_TAG = "chilc_s2_aspd"
_S2_DURATION = 10.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_FLAT, source_tag=_S2_BUFF_TAG))
    world.log(f"Chilc S2 — ASPD+{_S2_ASPD_FLAT:.0f}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_chilc(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Chilchuck"
    op.archetype = RoleArchetype.VAN_AGENT
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Lockpicks", slot="S1", sp_cost=12, initial_sp=9,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Improvisation", slot="S2", sp_cost=25, initial_sp=14,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
