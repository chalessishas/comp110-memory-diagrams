"""石棉 (Asbestos / Asbest) — 5★ Defender (Arts Protector archetype).

S1 "固守模式": sp_cost=20, initial_sp=0, duration=20s, MANUAL, AUTO_TIME.
  damage_scale: 0.7 (damage reduction) — not modeled.

S2 "火电模式": sp_cost=50, initial_sp=30, duration=50s, MANUAL, AUTO_TIME.
  ATK +90%, DEF +60%, base_attack_time +0.4s (slower attacks).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.asbest import make_asbest as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 stub ---
_S1_TAG = "asbest_s1_fortress_mode"
_S1_DURATION = 20.0

# --- S2 ---
_S2_TAG = "asbest_s2_fire_electric_mode"
_S2_ATK_RATIO = 0.90
_S2_DEF_RATIO = 0.60
_S2_INTERVAL_DELTA = 0.40
_S2_ATK_BUFF_TAG = "asbest_s2_atk"
_S2_DEF_BUFF_TAG = "asbest_s2_def"
_S2_INTERVAL_BUFF_TAG = "asbest_s2_interval"
_S2_DURATION = 50.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
        value=_S2_INTERVAL_DELTA, source_tag=_S2_INTERVAL_BUFF_TAG,
    ))
    world.log(f"Asbest S2 — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%} interval+{_S2_INTERVAL_DELTA:.2f}s/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG, _S2_INTERVAL_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_asbest(slot: str = "S2") -> UnitState:
    """Asbest E2 max. S1: damage reduction (not modeled). S2: ATK+90%+DEF+60%+interval+0.4s/50s."""
    op = _base_stats()
    op.name = "Asbest"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Fortress Mode",
            slot="S1",
            sp_cost=20,
            initial_sp=0,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Fire-Electric Mode",
            slot="S2",
            sp_cost=50,
            initial_sp=30,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
