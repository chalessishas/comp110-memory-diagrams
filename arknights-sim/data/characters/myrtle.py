"""Myrtle — 5* Vanguard (Standard Bearer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "Glistening" (E2): All Vanguards recover 25 HP/s while Myrtle is deployed.
S1 "Tactical Delivery I": 14 DP over 8s while not blocking (block=0 during skill).
  sp_cost=12, initial_sp=6, duration=8s, requires_target=False.
S2 "Healing Wings": 16 DP over 16s + heals most-injured adjacent ally at 50% ATK/s.
  sp_cost=18, initial_sp=9, duration=16s, requires_target=False.
  Heal range: cross (5-tile) centered on Myrtle.

Arknights wiki: Standard Bearer stops blocking during skill activation.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.myrtle import make_myrtle as _base_stats


STANDARD_BEARER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Glistening ---
_GLISTENING_TAG = "myrtle_glistening"
_GLISTENING_HEAL_RATE = 25.0   # HP/s to all Vanguards
_GLISTENING_FRAC_ATTR = "_myrtle_glistening_frac"


def _glistening_on_tick(world, carrier, dt: float) -> None:
    frac = getattr(carrier, _GLISTENING_FRAC_ATTR, 0.0) + _GLISTENING_HEAL_RATE * dt
    heal_amount = int(frac)
    if heal_amount > 0:
        for ally in world.allies():
            if ally.profession == Profession.VANGUARD and ally.hp < ally.max_hp:
                actual = ally.heal(heal_amount)
                world.global_state.total_healing_done += actual
    setattr(carrier, _GLISTENING_FRAC_ATTR, frac - heal_amount)


register_talent(_GLISTENING_TAG, on_tick=_glistening_on_tick)

_S1_TAG = "myrtle_s1_tactical_delivery"
_S1_DP_RATE = 14.0 / 8.0      # 1.75 DP/s over 8s duration
_S1_DP_FRAC_ATTR = "_myrtle_s1_dp_frac"


def _s1_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S1_DP_FRAC_ATTR, 0.0)


def _s1_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S1_DP_FRAC_ATTR, 0.0) + _S1_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S1_DP_FRAC_ATTR, frac - gained)


def _s1_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S1_DP_FRAC_ATTR, 0.0)


register_skill(_S1_TAG, on_start=_s1_on_start, on_tick=_s1_on_tick, on_end=_s1_on_end)


# ---------------------------------------------------------------------------
# S2 "Healing Wings"
# ---------------------------------------------------------------------------

_S2_TAG = "myrtle_s2_healing_wings"
_S2_DURATION = 16.0
_S2_DP_RATE  = 16.0 / _S2_DURATION   # 1.0 DP/s over 16s
_S2_HEAL_RATE = 0.50          # 50% ATK/s
_S2_DP_FRAC_ATTR   = "_myrtle_s2_dp_frac"
_S2_HEAL_FRAC_ATTR = "_myrtle_s2_heal_frac"

# Heal range: 5-tile cross around Myrtle (independent of her attack range_shape)
_S2_HEAL_RANGE = frozenset(((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)))


def _s2_find_heal_target(world, unit):
    """Most-injured (lowest HP%) ally within S2 heal range."""
    if unit.position is None:
        return None
    ox, oy = unit.position
    candidates = [
        u for u in world.allies()
        if u is not unit and u.alive and u.deployed
        and u.position is not None
        and (round(u.position[0]) - round(ox), round(u.position[1]) - round(oy)) in _S2_HEAL_RANGE
        and u.hp < u.max_hp
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda u: u.hp / u.max_hp)


def _s2_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)
    setattr(unit, _S2_HEAL_FRAC_ATTR, 0.0)


def _s2_on_tick(world, unit, dt: float) -> None:
    # DP drip
    dp_frac = getattr(unit, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    dp_gained = int(dp_frac)
    if dp_gained > 0:
        world.global_state.refund_dp(dp_gained)
    setattr(unit, _S2_DP_FRAC_ATTR, dp_frac - dp_gained)

    # HoT — 50% ATK/s applied to most-injured adjacent ally
    heal_frac = getattr(unit, _S2_HEAL_FRAC_ATTR, 0.0) + _S2_HEAL_RATE * unit.effective_atk * dt
    heal_amount = int(heal_frac)
    if heal_amount > 0:
        target = _s2_find_heal_target(world, unit)
        if target is not None:
            actual = target.heal(heal_amount)
            world.global_state.total_healing_done += actual
    setattr(unit, _S2_HEAL_FRAC_ATTR, heal_frac - heal_amount)


def _s2_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)
    setattr(unit, _S2_HEAL_FRAC_ATTR, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_myrtle(slot: str = "S1") -> UnitState:
    """Myrtle E2 max. Talent Glistening: +25 HP/s to Vanguards. S1/S2 DP drip."""
    op = _base_stats()
    op.name = "Myrtle"
    op.archetype = RoleArchetype.VAN_STANDARD_BEARER
    op.range_shape = STANDARD_BEARER_RANGE
    op.block = 1
    op.cost = 10
    op.talents = [TalentComponent(name="Glistening", behavior_tag=_GLISTENING_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Delivery I",
            slot="S1",
            sp_cost=12,
            initial_sp=6,
            duration=8.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Healing Wings",
            slot="S2",
            sp_cost=18,
            initial_sp=9,
            duration=16.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )

    return op
