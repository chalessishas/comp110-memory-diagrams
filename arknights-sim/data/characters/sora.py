"""Sora (空) — 4* Supporter (Bard archetype).

Bard Supporter trait: Never attacks. Instead, all allied operators within
  attack range recover +1 SP per second (continuous aura).
  Implemented as an on_tick talent: adds _SP_RATE × dt to each in-range ally's
  skill SP on every tick, as long as skill is not already active.

Talent "Mellow Flow" (E2): +0.5 additional SP/s bonus to the aura (total +1.5 SP/s).
  Also grants Inspiration: allies in range receive a flat ATK +_INSPIRATION_ATK bonus.
  Inspiration uses highest-wins semantics: multiple Bards deployed → only the largest
  Inspiration value applies to each ally (BuffStack.INSPIRATION in effective_stat).

S2 "Encore" (simplified): 20s duration; while active, Sora's SP aura doubles to +3 SP/s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_101_sora).
  HP=1356, ATK=385, DEF=258, RES=0, atk_interval=1.3s, cost=7, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.sora import make_sora as _base_stats


BARD_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# Bard trait: +1 SP/s to all allies in range
_TRAIT_TAG = "sora_bard_trait"
_TRAIT_SP_RATE = 1.0   # SP per second

# E2 talent: additional +0.5 SP/s bonus + Inspiration ATK aura
_TALENT_TAG = "sora_mellow_flow"
_TALENT_SP_BONUS = 0.5

# Inspiration: flat ATK buff pushed to in-range allies each tick (highest-wins)
# Sora E2 approximate: ~40 flat ATK (ArknightsGameData char_101_sora E2 rank)
_INSPIRATION_ATK = 40
_INSPIRATION_SOURCE_TAG = "sora_inspiration_atk"

# S2: doubles aura to +3 SP/s total while active
_S2_TAG = "sora_s2_encore"
_S2_DURATION = 20.0
_S2_SP_MULTIPLIER = 2.0   # 2× aura during S2
_S2_ACTIVE_FLAG = "sora_s2_active"


def _bard_sp_aura(world, carrier: UnitState, dt: float, sp_rate: float) -> None:
    """Distribute sp_rate SP/s to all in-range allies with uncharged skills."""
    if not carrier.deployed or carrier.position is None:
        return
    s2_active = carrier.skill is not None and carrier.skill.active_remaining > 0
    effective_rate = sp_rate * (_S2_SP_MULTIPLIER if s2_active else 1.0)
    now = world.global_state.elapsed
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if ally.skill is None or ally.skill.active_remaining > 0:
            continue
        if now < ally.skill.sp_lockout_until:
            continue
        if not _ally_in_range(carrier, ally):
            continue
        ally.skill.sp = min(ally.skill.sp + effective_rate * dt, float(ally.skill.sp_cost))


def _ally_in_range(op: UnitState, ally: UnitState) -> bool:
    if op.position is None or ally.position is None:
        return False
    ox, oy = op.position
    ax, ay = ally.position
    dx_int = round(ax) - round(ox)
    dy_int = round(ay) - round(oy)
    return (dx_int, dy_int) in set(op.range_shape.tiles)


def _trait_on_tick(world, carrier: UnitState, dt: float) -> None:
    _bard_sp_aura(world, carrier, dt, _TRAIT_SP_RATE)


def _push_inspiration(world, carrier: UnitState) -> None:
    """Push flat ATK Inspiration buff to each in-range ally (replace each tick)."""
    if not carrier.deployed or carrier.position is None:
        return
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not _ally_in_range(carrier, ally):
            continue
        ally.buffs = [b for b in ally.buffs if b.source_tag != _INSPIRATION_SOURCE_TAG]
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.INSPIRATION,
            value=float(_INSPIRATION_ATK), source_tag=_INSPIRATION_SOURCE_TAG,
        ))


def _remove_inspiration(world, carrier: UnitState) -> None:
    """Remove Sora's Inspiration buff from all allies on death or retreat."""
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _INSPIRATION_SOURCE_TAG]


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    _bard_sp_aura(world, carrier, dt, _TALENT_SP_BONUS)
    _push_inspiration(world, carrier)


register_talent(_TRAIT_TAG, on_tick=_trait_on_tick)
register_talent(
    _TALENT_TAG,
    on_tick=_talent_on_tick,
    on_death=_remove_inspiration,
    on_retreat=_remove_inspiration,
)


def _s2_on_start(world, carrier: UnitState) -> None:
    world.log(f"{carrier.name} S2 Encore active — SP aura ×{_S2_SP_MULTIPLIER}")


def _s2_on_end(world, carrier: UnitState) -> None:
    world.log(f"{carrier.name} S2 Encore ended")


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_sora(slot: str = "S2", talent: bool = True) -> UnitState:
    """Sora E2 max. Bard: +1 SP/s aura to allies. talent=True adds Mellow Flow +0.5 SP/s."""
    op = _base_stats()
    op.name = "Sora"
    op.archetype = RoleArchetype.SUP_BARD
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS  # unused (Bard never attacks)
    op.attack_range_melee = False
    op.range_shape = BARD_RANGE
    op.block = 1
    op.cost = 7

    talents = [TalentComponent(name="Bard Trait", behavior_tag=_TRAIT_TAG)]
    if talent:
        talents.append(TalentComponent(name="Mellow Flow", behavior_tag=_TALENT_TAG))
    op.talents = talents

    if slot == "S2":
        op.skill = SkillComponent(
            name="Encore",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
