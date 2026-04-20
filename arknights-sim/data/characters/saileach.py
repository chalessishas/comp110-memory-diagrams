"""Saileach (铸铁) — 6* Vanguard (Standard Bearer archetype).

S1 "Tactical Deployment I": 14 DP over 8s (same rate as Myrtle S1).
  sp_cost=22, initial_sp=11, duration=8s, block=0 during skill.

S2 "Flagship Order": 20 DP over 20s + global HoT at 35% ATK/s to all allies.
  sp_cost=35, initial_sp=20, duration=20s, block=0 during skill.
  No range restriction on HoT — heals all deployed alive allies.

S3 "Battle Hymn": 30 DP over 20s + ATK+40% to all deployed allies.
  sp_cost=40, initial_sp=20, duration=20s, MANUAL, block=0 during skill.
  Team ATK buff applied on_start, cleared on_end.

Base stats: E2 max, trust 100 (from generated/sidero.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    BuffAxis, BuffStack, Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.sidero import make_sidero as _base_stats


# --- Talent: Vanguard's Ruse ---
_VANGUARDS_RUSE_TAG = "saileach_vanguards_ruse"
_SP_GRANT = 2.0    # E2 max: +2 SP to all deployed Vanguard allies at battle start


def _vanguards_ruse_on_battle_start(world, carrier: UnitState) -> None:
    for ally in world.allies():
        if not ally.deployed or not ally.alive:
            continue
        if ally.profession != Profession.VANGUARD:
            continue
        sk = ally.skill
        if sk is None:
            continue
        sk.sp = min(sk.sp + _SP_GRANT, float(sk.sp_cost))


register_talent(_VANGUARDS_RUSE_TAG, on_battle_start=_vanguards_ruse_on_battle_start)


STANDARD_BEARER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# ---------------------------------------------------------------------------
# S1 "Tactical Deployment I"
# ---------------------------------------------------------------------------
_S1_TAG = "saileach_s1_tactical_deployment"
_S1_DP_RATE = 14.0 / 8.0          # 1.75 DP/s
_S1_DP_FRAC = "_saileach_s1_dp_frac"


def _s1_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S1_DP_FRAC, 0.0)


def _s1_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S1_DP_FRAC, 0.0) + _S1_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S1_DP_FRAC, frac - gained)


def _s1_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S1_DP_FRAC, 0.0)


register_skill(_S1_TAG, on_start=_s1_on_start, on_tick=_s1_on_tick, on_end=_s1_on_end)


# ---------------------------------------------------------------------------
# S2 "Flagship Order"
# ---------------------------------------------------------------------------
_S2_TAG = "saileach_s2_flagship_order"
_S2_DP_RATE   = 20.0 / 20.0    # 1.0 DP/s over 20s
_S2_HEAL_RATE = 0.35            # 35% ATK/s global
_S2_DP_FRAC   = "_saileach_s2_dp_frac"
_S2_HEAL_FRAC = "_saileach_s2_heal_frac"


def _s2_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S2_DP_FRAC, 0.0)
    setattr(unit, _S2_HEAL_FRAC, 0.0)


def _s2_on_tick(world, unit, dt: float) -> None:
    # DP drip
    dp_frac = getattr(unit, _S2_DP_FRAC, 0.0) + _S2_DP_RATE * dt
    dp_gained = int(dp_frac)
    if dp_gained > 0:
        world.global_state.refund_dp(dp_gained)
    setattr(unit, _S2_DP_FRAC, dp_frac - dp_gained)

    # Global HoT — 35% ATK/s, no range restriction
    heal_frac = getattr(unit, _S2_HEAL_FRAC, 0.0) + _S2_HEAL_RATE * unit.effective_atk * dt
    heal_amount = int(heal_frac)
    if heal_amount > 0:
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp:
                continue
            actual = ally.heal(heal_amount)
            world.global_state.total_healing_done += actual
    setattr(unit, _S2_HEAL_FRAC, heal_frac - heal_amount)


def _s2_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S2_DP_FRAC, 0.0)
    setattr(unit, _S2_HEAL_FRAC, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


# ---------------------------------------------------------------------------
# S3 "Battle Hymn" — 30 DP/20s + ATK+40% to all deployed allies
# ---------------------------------------------------------------------------
_S3_TAG = "saileach_s3_battle_hymn"
_S3_DP_RATE    = 30.0 / 20.0   # 1.5 DP/s over 20s
_S3_ATK_RATIO  = 0.40           # ATK +40% to all deployed allies
_S3_BUFF_TAG   = "saileach_s3_atk"
_S3_DP_FRAC    = "_saileach_s3_dp_frac"


def _s3_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S3_DP_FRAC, 0.0)
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
        ))


def _s3_on_tick(world, unit, dt: float) -> None:
    dp_frac = getattr(unit, _S3_DP_FRAC, 0.0) + _S3_DP_RATE * dt
    dp_gained = int(dp_frac)
    if dp_gained > 0:
        world.global_state.refund_dp(dp_gained)
    setattr(unit, _S3_DP_FRAC, dp_frac - dp_gained)


def _s3_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S3_DP_FRAC, 0.0)
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_saileach(slot: str = "S2") -> UnitState:
    """Saileach E2 max, trust 100.
    S1: 14 DP/8s Standard Bearer drip.
    S2: 20 DP/20s + global 35% ATK/s HoT.
    """
    op = _base_stats()
    op.name = "Saileach"
    op.archetype = RoleArchetype.VAN_STANDARD_BEARER
    op.profession = Profession.VANGUARD
    op.range_shape = STANDARD_BEARER_RANGE
    op.block = 1
    op.cost = 23
    op.talents = [TalentComponent(name="Vanguard's Ruse", behavior_tag=_VANGUARDS_RUSE_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Deployment I",
            slot="S1",
            sp_cost=22,
            initial_sp=11,
            duration=8.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Flagship Order",
            slot="S2",
            sp_cost=35,
            initial_sp=20,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Battle Hymn",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
