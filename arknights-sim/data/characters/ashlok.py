"""灰毫 (Ashlok) — 5★ Defender.

S1 "攻击力强化·γ型" (shared): sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +100%.

S2 "专注轰击": sp_cost=18, initial_sp=10, duration=10s, MANUAL, AUTO_TIME.
  ATK +55%, base_attack_time -0.65s (flat interval reduction).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.ashlok import make_ashlok as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 ---
_S1_TAG = "ashlok_s1_atk_up"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "ashlok_s1_atk"
_S1_DURATION = 30.0

# --- S2 ---
_S2_TAG = "ashlok_s2_focus_shot"
_S2_ATK_RATIO = 0.55
_S2_INTERVAL_DELTA = -0.65
_S2_ATK_BUFF_TAG = "ashlok_s2_atk"
_S2_INTERVAL_BUFF_TAG = "ashlok_s2_interval"
_S2_DURATION = 10.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Ashlok S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=_S2_INTERVAL_DELTA, source_tag=_S2_INTERVAL_BUFF_TAG,
    ))
    world.log(f"Ashlok S2 — ATK+{_S2_ATK_RATIO:.0%} interval{_S2_INTERVAL_DELTA:+.2f}s/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_INTERVAL_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_ashlok(slot: str = "S1") -> UnitState:
    """Ashlok E2 max. S1: ATK+100%/30s. S2: ATK+55%+interval-0.65s/10s."""
    op = _base_stats()
    op.name = "Ashlok"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ",
            slot="S1",
            sp_cost=30,
            initial_sp=15,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Focused Bombardment",
            slot="S2",
            sp_cost=18,
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
