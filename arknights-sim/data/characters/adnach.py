"""Adnachiel (安德切尔) — 3* Sniper (Marksman archetype).

Talent "Marksman Mastery" (短板突破): ASPD +8 while deployed.

S1 "ATK Up α" (攻击力强化·α型): ATK +50% for 20s.
  sp_cost=40, initial_sp=0, MANUAL, AUTO_TIME.

Base stats from ArknightsGameData (E1 max, trust 100).
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
from data.characters.generated.adnach import make_adnach as _base_stats


MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

# --- Talent: Marksman Mastery ---
_TALENT_TAG = "adnach_marksman_mastery"
_TALENT_BUFF_TAG = "adnach_aspd_passive"
_TALENT_ASPD_BONUS = 8.0


def _talent_on_deploy(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_TALENT_ASPD_BONUS, source_tag=_TALENT_BUFF_TAG,
    ))


register_talent(_TALENT_TAG, on_deploy=_talent_on_deploy)

# --- S1: ATK Up α ---
_S1_TAG = "adnach_s1_atk_up"
_S1_ATK_RATIO = 0.50
_S1_BUFF_TAG = "adnach_s1_atk"
_S1_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Adnachiel S1 ATK Up α — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_adnach(slot: str = "S1") -> UnitState:
    """Adnachiel E1 max. Talent: ASPD+8 passive. S1: ATK+50%/20s."""
    op = _base_stats()
    op.name = "Adnachiel"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MARKSMAN_RANGE
    op.talents = [TalentComponent(name="Marksman Mastery", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up α",
            slot="S1",
            sp_cost=40,
            initial_sp=0,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    return op
