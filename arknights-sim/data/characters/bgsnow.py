"""Hongxue (鸿雪) — 5★ Sniper (Heavyshooter archetype).

S1 "ATK Up γ" (conservative): sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +80%.

S2 "Burst Shot" (conservative): sp_cost=40, initial_sp=20, duration=25s, MANUAL, AUTO_TIME.
  ATK +120%.

Note: Hongxue has a typewriter-deployable mechanic in-game (complex summon);
  summon interaction not modeled here.

Base stats from ArknightsGameData (E2 max, trust 100, char_4055_bgsnow).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.bgsnow import make_bgsnow as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "bgsnow_s1_atk_up"
_S1_ATK_RATIO = 0.80
_S1_BUFF_TAG = "bgsnow_s1_atk"
_S1_DURATION = 30.0
_S2_TAG = "bgsnow_s2_burst_shot"
_S2_ATK_RATIO = 1.20
_S2_BUFF_TAG = "bgsnow_s2_atk"
_S2_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Hongxue S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Hongxue S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_bgsnow(slot: str = "S1") -> UnitState:
    """Hongxue E2 max. Heavyshooter Sniper. S1: ATK+80%/30s. S2: ATK+120%/25s."""
    op = _base_stats()
    op.name = "Hongxue"
    op.archetype = RoleArchetype.SNIPER_HEAVY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Burst Shot", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
