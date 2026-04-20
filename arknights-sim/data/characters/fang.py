"""Fang — 4* Vanguard (Charger archetype).

Base stats from ArknightsGameData (E1 max, trust 100).
Charger class trait: gains 1 DP when this unit kills an enemy.

S1 "Assault": ATK +50% for 40s.
  sp_cost=25, initial_sp=0, AUTO_TIME, AUTO trigger, requires_target=True.

S2 "Assault Formation": 20 DP over 15s (DP drip), block=0 during skill.
  sp_cost=30, initial_sp=0, AUTO_TIME, AUTO trigger, requires_target=False.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.fang import make_fang as _base_stats


CHARGER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_CHARGER_DP_TAG = "vanguard_charger_dp_on_kill"


def _on_kill(world, killer, killed) -> None:
    if killed.faction.value == "enemy":
        world.global_state.refund_dp(1)


register_talent(_CHARGER_DP_TAG, on_kill=_on_kill)


# --- S1: Assault ---
_S1_TAG = "fang_s1_assault"
_S1_ATK_RATIO = 0.50     # ATK +50%
_S1_SOURCE_TAG = "fang_s1_assault"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_SOURCE_TAG,
    ))
    world.log(f"Fang S1 Assault — ATK +{_S1_ATK_RATIO:.0%}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_SOURCE_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


# --- S2: Assault Formation — 20 DP / 15s drip, block=0 ---
_S2_TAG = "fang_s2_assault_formation"
_S2_DP_TOTAL = 20
_S2_DURATION = 15.0
_S2_DP_RATE = _S2_DP_TOTAL / _S2_DURATION   # 4/3 DP/s
_S2_DP_FRAC_ATTR = "_fang_s2_dp_frac"


def _s2_on_start(world, unit: UnitState) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)
    world.log(f"Fang S2 Assault Formation — {_S2_DP_TOTAL} DP / {_S2_DURATION}s, block=0")


def _s2_on_tick(world, unit: UnitState, dt: float) -> None:
    frac = getattr(unit, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S2_DP_FRAC_ATTR, frac - gained)


def _s2_on_end(world, unit: UnitState) -> None:
    unit.block = getattr(unit, "_saved_block", 2)
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)
    world.log("Fang S2 ended — block restored")


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_fang(slot: str = "S1") -> UnitState:
    """Fang E1 max. Charger: +1 DP on kill. S1: ATK+50% 40s. S2: 20 DP / 15s drip."""
    op = _base_stats()
    op.name = "Fang"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.range_shape = CHARGER_RANGE
    op.block = 2
    op.cost = 11
    op.talents = [TalentComponent(
        name="Charger (DP on kill)",
        behavior_tag=_CHARGER_DP_TAG,
    )]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Assault",
            slot="S1",
            sp_cost=25,
            initial_sp=0,
            duration=40.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Assault Formation",
            slot="S2",
            sp_cost=30,
            initial_sp=0,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
