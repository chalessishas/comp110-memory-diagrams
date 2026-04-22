"""Cuora (草蛇) — 4★ Defender (Protector).

S1 "DEF Up β" (shared): sp_cost=35, initial_sp=10, duration=35s, MANUAL, AUTO_TIME.
  DEF +80%.

S2 "Shell Defense": sp_cost=40, initial_sp=0, duration=30s, MANUAL, AUTO_TIME.
  DEF +130%, block +1, HP regen 3%/s (regen not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.snakek import make_snakek as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "snakek_s1_def_up"
_S1_DEF_RATIO = 0.80
_S1_BUFF_TAG = "snakek_s1_def"
_S1_DURATION = 35.0
_S2_TAG = "snakek_s2_shell_defense"
_S2_DEF_RATIO = 1.30
_S2_BLOCK_BONUS = 1
_S2_DEF_BUFF_TAG = "snakek_s2_def"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Snakek S1 — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG))
    carrier.block += _S2_BLOCK_BONUS
    world.log(f"Snakek S2 — DEF+{_S2_DEF_RATIO:.0%} block+{_S2_BLOCK_BONUS}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_BUFF_TAG]
    carrier.block -= _S2_BLOCK_BONUS


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)
register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_snakek(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Snakek"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="DEF Up β", slot="S1", sp_cost=35, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Shell Defense", slot="S2", sp_cost=40, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
