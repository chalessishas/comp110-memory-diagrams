"""Toknogi (月禾) — 5★ Supporter (Abjurer archetype).

SUP_ABJURER trait: Protects nearby allies — grants them a passive DEF bonus
  while Toknogi is deployed on the field.

Talent "Spring Green Shade": All allies within _TALENT_RANGE tiles gain
  DEF +_TALENT_DEF_RATIO (ratio). Buff is applied/removed dynamically each tick
  based on distance.

S2 "Grove Shade": MANUAL.
  Self ATK +_S2_ATK_RATIO for _S2_DURATION seconds.
  Also applies DEF +_S2_DEF_RATIO to all allies within _S2_RANGE tiles.
  sp_cost=30, initial_sp=15, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100, char_343_tknogi):
  HP=2020, ATK=485, DEF=175, RES=25, atk_interval=1.6s, cost=12, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.tknogi import make_tknogi as _base_stats


ABJURER_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1), (2, -1), (2, 1)))

_TALENT_TAG = "toknogi_spring_shade"
_TALENT_DEF_RATIO = 0.20
_TALENT_DEF_TAG = "toknogi_talent_def"
_TALENT_RANGE = 2              # Manhattan distance threshold

_S2_TAG = "toknogi_s2_grove_shade"
_S2_ATK_RATIO = 0.30
_S2_ATK_BUFF_TAG = "toknogi_s2_atk"
_S2_DEF_RATIO = 0.35
_S2_DEF_BUFF_TAG = "toknogi_s2_def"
_S2_RANGE = 3
_S2_DURATION = 20.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    cx, cy = carrier.position
    for ally in world.allies():
        if ally is carrier or ally.position is None:
            continue
        ax, ay = ally.position
        in_range = (abs(ax - cx) + abs(ay - cy) <= _TALENT_RANGE)
        has_buff = any(b.source_tag == _TALENT_DEF_TAG for b in ally.buffs)
        if in_range and not has_buff:
            ally.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                value=_TALENT_DEF_RATIO, source_tag=_TALENT_DEF_TAG,
            ))
        elif not in_range and has_buff:
            ally.buffs = [b for b in ally.buffs if b.source_tag != _TALENT_DEF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    if carrier.position is None:
        return
    cx, cy = carrier.position
    for ally in world.allies():
        if ally is carrier or ally.position is None:
            continue
        ax, ay = ally.position
        if abs(ax - cx) + abs(ay - cy) <= _S2_RANGE:
            ally.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
            ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S2_DEF_BUFF_TAG]
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# S3: Ancient Forest — ATK+80%, DEF+60% to ALL deployed allies
_S3_TAG = "toknogi_s3_ancient_forest"
_S3_ATK_RATIO = 0.80
_S3_ATK_BUFF_TAG = "toknogi_s3_atk"
_S3_DEF_RATIO = 0.60
_S3_DEF_BUFF_TAG = "toknogi_s3_def"
_S3_DURATION = 25.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=_S3_DEF_RATIO, source_tag=_S3_DEF_BUFF_TAG,
        ))
    world.log(f"Toknogi S3 Ancient Forest — ATK+{_S3_ATK_RATIO:.0%}, DEF+{_S3_DEF_RATIO:.0%} all allies")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_DEF_BUFF_TAG]
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_DEF_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_toknogi(slot: str = "S2") -> UnitState:
    """Toknogi E2 max. Talent: DEF+20% nearby allies. S2: ATK+30%+DEF+35%. S3: ATK+80%+DEF+60% all allies."""
    op = _base_stats()
    op.name = "Toknogi"
    op.archetype = RoleArchetype.SUP_ABJURER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = ABJURER_RANGE
    op.block = 1
    op.cost = 12

    op.talents = [TalentComponent(name="Spring Green Shade", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Grove Shade",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Ancient Forest",
            slot="S3",
            sp_cost=40,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
