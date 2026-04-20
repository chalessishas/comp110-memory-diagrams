"""Dur-nar (坚雷) — 5★ Defender (Arts Protector archetype).

DEF_ARTS_PROTECTOR trait: Attacks deal Arts damage to blocked enemies instead
  of physical damage. Retains full Defender block-3 capability. Since ATK is
  compared against enemy RES (not DEF), this archetype excels against armored
  enemies that have low Arts resistance.

Talent "Thunder Strike": When 2 or more enemies are currently being blocked by
  Dur-nar, gain ATK+20%. Applied each tick while the condition holds; removed
  when blocking count drops below threshold.

S2 "Iron Defense": 25s duration. DEF+50% and block count increases from 3 to 4.
  Allows Dur-nar to hold an additional enemy lane while gaining tankiness.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_260_durnar).
  HP=3007, ATK=648, DEF=548, RES=15, atk_interval=1.6s, cost=24, block=3.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.durnar import make_durnar as _base_stats


ARTS_PROTECTOR_RANGE = RangeShape(tiles=((0, 0),))

# Talent: Thunder Strike
_TALENT_TAG = "durnar_thunder_strike"
_TALENT_BUFF_TAG = "durnar_talent_atk"
_TALENT_ATK_RATIO = 0.20      # +20% ATK when 2+ enemies blocked
_TALENT_THRESHOLD = 2          # min blocked enemies to activate

# S2: Iron Defense
_S2_TAG = "durnar_s2_iron_defense"
_S2_DEF_RATIO = 0.50           # +50% DEF
_S2_DEF_BUFF_TAG = "durnar_s2_def"
_S2_BASE_BLOCK = 3
_S2_BLOCK_BONUS = 1            # +1 block → total 4
_S2_DURATION = 25.0


def _blocking_count(carrier: UnitState, world) -> int:
    return sum(
        1 for e in world.enemies()
        if e.alive and carrier.unit_id in e.blocked_by_unit_ids
    )


def _thunder_on_tick(world, carrier: UnitState, dt: float) -> None:
    count = _blocking_count(carrier, world)
    has_buff = any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs)
    if count >= _TALENT_THRESHOLD:
        if not has_buff:
            carrier.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
            ))
    else:
        if has_buff:
            carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_thunder_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.block = _S2_BASE_BLOCK + _S2_BLOCK_BONUS
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.block = _S2_BASE_BLOCK
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_durnar(slot: str = "S2") -> UnitState:
    """Dur-nar E2 max. DEF_ARTS_PROTECTOR: Arts damage, block-3. S2: +50% DEF + block-4."""
    op = _base_stats()
    op.name = "Dur-nar"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = True
    op.range_shape = ARTS_PROTECTOR_RANGE
    op.block = 3
    op.cost = 24

    op.talents = [TalentComponent(name="Thunder Strike", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Iron Defense",
            slot="S2",
            sp_cost=40,
            initial_sp=20,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
