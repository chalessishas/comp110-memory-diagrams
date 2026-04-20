"""Exusiai — 6* Sniper (Marksman archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Only Orange II": +100 ASPD for 30s (sp_cost=5, initial=3) — halves attack interval.
S3 "Light-Speed Strike II": ATK+70%, ASPD+20, ATK_INTERVAL -0.40s for 40s.
  sp_cost=50, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.
  Combined formula: max(0.067, (1.0 - 0.4) * 100/(100+20)) ≈ 0.50s interval.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.exusiai import make_exusiai as _base_stats


# --- Talent: Eagle Eye ---
_EAGLE_EYE_TAG = "exusiai_eagle_eye"
_CRIT_CHANCE = 0.15    # E2 max: 15% crit on all attacks


def _eagle_eye_on_battle_start(world, carrier: UnitState) -> None:
    carrier.crit_chance = _CRIT_CHANCE


register_talent(_EAGLE_EYE_TAG, on_battle_start=_eagle_eye_on_battle_start)


MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S2_TAG = "exusiai_s2_only_orange"
_S2_ASPD_BONUS = 100.0
_S2_BUFF_TAG = "exusiai_s2_aspd"

_S3_TAG = "exusiai_s3_light_speed_strike"
_S3_ATK_RATIO = 0.70          # +70% ATK
_S3_ASPD_BONUS = 20.0         # +20 ASPD
_S3_INTERVAL_OFFSET = -0.40   # -0.40s flat ATK_INTERVAL (pre-ASPD-scale)
_S3_ATK_BUFF_TAG = "exusiai_s3_atk"
_S3_ASPD_BUFF_TAG = "exusiai_s3_aspd"
_S3_INTERVAL_BUFF_TAG = "exusiai_s3_interval"
_S3_DURATION = 40.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_BONUS, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.extend([
        Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
             value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG),
        Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
             value=_S3_ASPD_BONUS, source_tag=_S3_ASPD_BUFF_TAG),
        Buff(axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
             value=_S3_INTERVAL_OFFSET, source_tag=_S3_INTERVAL_BUFF_TAG),
    ])


def _s3_on_end(world, carrier: UnitState) -> None:
    tags = {_S3_ATK_BUFF_TAG, _S3_ASPD_BUFF_TAG, _S3_INTERVAL_BUFF_TAG}
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in tags]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_exusiai(slot: str = "S2") -> UnitState:
    """Exusiai E2 max, trust 100. Base stats from akgd; S2 and S3 wired."""
    op = _base_stats()
    op.name = "Exusiai"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.range_shape = MARKSMAN_RANGE
    op.cost = 16
    op.talents = [TalentComponent(name="Eagle Eye", behavior_tag=_EAGLE_EYE_TAG)]
    if slot == "S2":
        op.skill = SkillComponent(
            name="Only Orange",
            slot="S2",
            sp_cost=5,
            initial_sp=3,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Light-Speed Strike",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            behavior_tag=_S3_TAG,
        )
    return op
