"""Hoshiguma — 6* Defender (Juggernaut archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "Overweight": when HP > 50%, reduce damage taken by 20% (E2 rank).
Skill S2 "Unshakeable" (rank VII, E2):
  DEF +300 for 20s. AUTO_TIME, AUTO trigger. sp_cost=40.
  Classic Liskarm synergy target: Liskarm's SP battery charges this skill.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.hoshiguma import make_hoshiguma as _base_stats


DEFENDER_MELEE_BLOCK3 = RangeShape(tiles=((0, 0),))

_OVERWEIGHT_TAG = "hoshiguma_overweight"

_S2_TAG = "hoshiguma_s2_unshakeable"
_S2_DEF_TAG = "hoshiguma_s2_def"
_S2_DEF_FLAT = 300   # rank VII approximate (+300 DEF for 20s)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_S2_DEF_FLAT, source_tag=_S2_DEF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_hoshiguma() -> UnitState:
    """Hoshiguma E2 max, trust 100. Overweight talent + S2 Unshakeable."""
    op = _base_stats()
    op.name = "Hoshiguma"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.range_shape = DEFENDER_MELEE_BLOCK3
    op.cost = 23
    op.talents = [TalentComponent(
        name="Overweight",
        behavior_tag=_OVERWEIGHT_TAG,
        params={"reduction": 0.20, "hp_threshold": 0.5},
    )]
    op.skill = SkillComponent(
        name="Unshakeable", slot="S2",
        sp_cost=40, initial_sp=0, duration=20.0,
        sp_gain_mode=SPGainMode.AUTO_TIME,
        trigger=SkillTrigger.AUTO,
        requires_target=False,   # pure self-buff, fires regardless of targeting
        behavior_tag=_S2_TAG,
    )
    op.skill.sp = 0.0
    return op
