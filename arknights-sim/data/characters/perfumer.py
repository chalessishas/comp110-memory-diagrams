"""Perfumer (调香师) — 5* Medic (Ring-healer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "熏衣香" (E2): While deployed, all allies recover HP equal to
  5% of Perfumer's ATK per second (global passive HoT, no range restriction).

S2 "Soothing Fume": ATK +100% for 20s — doubles both targeted heal and passive HoT.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.flower import make_flower as _base_stats


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)
))

_PASSIVE_TAG = "perfumer_passive_hot"
_HEAL_RATE = 0.05   # 5% of ATK per second (E2 talent)
_ACCUM_KEY = "_perfumer_hot_accum"


def _on_tick(world, perfumer: UnitState, dt: float) -> None:
    """Accumulate fractional heal; apply integer HP to all alive deployed allies."""
    accum = getattr(perfumer, _ACCUM_KEY, 0.0) + perfumer.effective_atk * _HEAL_RATE * dt
    whole = int(accum)
    if whole > 0:
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp:
                continue
            healed = ally.heal(whole)
            world.global_state.total_healing_done += healed
    setattr(perfumer, _ACCUM_KEY, accum - whole)


register_talent(_PASSIVE_TAG, on_tick=_on_tick)


# --- S2: Soothing Fume ---
_S2_TAG = "perfumer_s2_soothing_fume"
_S2_ATK_RATIO = 1.00     # ATK +100% — doubles targeted heal and passive HoT
_S2_SOURCE_TAG = "perfumer_s2_soothing_fume"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    world.log(f"Perfumer S2 Soothing Fume — ATK +{_S2_ATK_RATIO:.0%}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_perfumer(slot: str = "S2") -> UnitState:
    """Perfumer E2 max, trust 100. Passive HoT: all allies +5% ATK HP/s. S2: ATK+100% 20s."""
    op = _base_stats()
    op.name = "Perfumer"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 16
    op.talents = [TalentComponent(
        name="Lavender (passive HoT)",
        behavior_tag=_PASSIVE_TAG,
    )]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Soothing Fume",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
