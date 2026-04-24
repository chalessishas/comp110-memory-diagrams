"""Firewatch (守林人) — 5★ Sniper (Deadeye).

S1 "Camouflage": sp_cost=26, initial_sp=0, duration=35s, AUTO_TIME, AUTO.
  ATK +40%. Invisibility not modeled (no combat effect in sim).
S2 "Tactical Transceiver": sp_cost=50, initial_sp=20, instant, AUTO_TIME, MANUAL.
  Launches 2 AoE bombs (240% ATK each). Not modeled — complex strike mechanic.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.milu import make_milu as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))

# --- S1 ---
_S1_TAG = "milu_s1_camouflage"
_S1_ATK_RATIO = 0.40
_S1_BUFF_TAG = "milu_s1_atk"
_S1_DURATION = 35.0

# --- S2 ---
_S2_TAG = "milu_s2"; _S2_DURATION = 0.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Firewatch S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_milu(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Firewatch"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Camouflage", slot="S1", sp_cost=26, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Tactical Transceiver", slot="S2", sp_cost=50, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
