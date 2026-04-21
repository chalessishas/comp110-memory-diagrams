"""赤冬 (Akafuyu) — 5★ Guard (Fighter archetype).

S1 "信影流·雷刀之势": sp_cost=16, initial_sp=0, duration=12s, MANUAL, AUTO_TIME.
  ATK +80%.

S2 "信影流·十文字胜": sp_cost=25, initial_sp=15, duration=20s, MANUAL, AUTO_TIME.
  ATK +100%, DEF +120%. (hp_ratio condition not modeled.)
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.akafyu import make_akafyu as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 ---
_S1_TAG = "akafyu_s1_raito"
_S1_ATK_RATIO = 0.80
_S1_BUFF_TAG = "akafyu_s1_atk"
_S1_DURATION = 12.0

# --- S2 ---
_S2_TAG = "akafyu_s2_jumonji"
_S2_ATK_RATIO = 1.00
_S2_DEF_RATIO = 1.20
_S2_ATK_BUFF_TAG = "akafyu_s2_atk"
_S2_DEF_BUFF_TAG = "akafyu_s2_def"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Akafuyu S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    world.log(f"Akafuyu S2 — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_akafyu(slot: str = "S1") -> UnitState:
    """Akafuyu E2 max. S1: ATK+80%/12s. S2: ATK+100%+DEF+120%/20s."""
    op = _base_stats()
    op.name = "Akafuyu"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Raito no Kamae",
            slot="S1",
            sp_cost=16,
            initial_sp=0,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Jumonji",
            slot="S2",
            sp_cost=25,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
