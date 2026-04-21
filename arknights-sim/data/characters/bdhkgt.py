"""截云 (Bdhkgt / "Zhe Yun") — 5★ Sniper.

S1 "探前路": sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +80%, ASPD +20.

S2 "重镞穿林": sp_cost=25, initial_sp=10, duration=15s, MANUAL, AUTO_TIME.
  ATK×135% per hit + move_speed slow on enemies (not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.bdhkgt import make_bdhkgt as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

# --- S1 ---
_S1_TAG = "bdhkgt_s1_scout_path"
_S1_ATK_RATIO = 0.80
_S1_ASPD_BONUS = 20.0
_S1_ATK_BUFF_TAG = "bdhkgt_s1_atk"
_S1_ASPD_BUFF_TAG = "bdhkgt_s1_aspd"
_S1_DURATION = 30.0

# --- S2 ---
_S2_TAG = "bdhkgt_s2_heavy_bolt"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG,
    ))
    world.log(f"Bdhkgt S1 — ATK+{_S1_ATK_RATIO:.0%} ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_bdhkgt(slot: str = "S1") -> UnitState:
    """Bdhkgt E2 max. S1: ATK+80%+ASPD+20/30s. S2: ATK×135% (not modeled)."""
    op = _base_stats()
    op.name = "Bdhkgt"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Scout Path",
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
            name="Heavy Bolt Through Trees",
            slot="S2",
            sp_cost=25,
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
