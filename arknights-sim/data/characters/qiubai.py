"""Qiubai (仇白) — 6★ Guard (Centurion archetype).

GUARD_CENTURION trait: Each attack hits all currently-blocked enemies.

Talent "Feathered Gale" (E2): Every 3rd consecutive attack on the same enemy
  triggers a True damage burst = _SEAL_TRUE_DMG_RATIO × ATK.
  Seal count is per-target, tracked as a lazy attribute _QIUBAI_SEAL_ATTR.
  Different enemies have independent counters; counter resets to 0 after burst.

S3 "Soulwind": ATK +150%, block→3, 30s duration.
  sp_cost=50, initial_sp=25, AUTO_TIME, AUTO trigger, requires_target=False.
  On end: ATK buff removed, block reverts to 2.

Constants from arknights.wiki.gg/wiki/Qiubai (M3 values).
Base stats from ArknightsGameData (E2 max, trust 100, char_4082_qiubai).
  HP=2480, ATK=768, DEF=452, RES=10, atk_interval=1.3s, cost=20, block=2.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.qiubai import make_qiubai as _base_stats


CENTURION_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_SEAL_TAG = "qiubai_feathered_gale"
_SEAL_ATTR = "_qiubai_seals"   # lazy int attribute on enemy UnitState
_SEAL_MAX = 3
_SEAL_TRUE_DMG_RATIO = 1.80    # 180% ATK True damage on 3rd seal (wiki M3)

# --- S2: Wind Slash ---
_S2_TAG = "qiubai_s2_wind_slash"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "qiubai_s2_atk"
_S2_DURATION = 20.0

_S3_TAG = "qiubai_s3_soulwind"
_S3_ATK_RATIO = 1.50
_S3_BUFF_TAG = "qiubai_s3_atk"
_S3_BLOCK = 3
_S3_DURATION = 30.0


def _galeforce_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    seals = getattr(target, _SEAL_ATTR, 0) + 1
    if seals >= _SEAL_MAX:
        true_dmg = int(attacker.effective_atk * _SEAL_TRUE_DMG_RATIO)
        dealt = target.take_true(true_dmg)
        world.global_state.total_damage_dealt += dealt
        setattr(target, _SEAL_ATTR, 0)
        world.log(f"Qiubai Feathered Gale burst → {target.name}  true={dealt}")
    else:
        setattr(target, _SEAL_ATTR, seals)


register_talent(_SEAL_TAG, on_attack_hit=_galeforce_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Qiubai S2 Wind Slash — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.block = _S3_BLOCK
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.block = 2
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_qiubai(slot: str = "S3") -> UnitState:
    """Qiubai E2 max. Centurion: hits all blocked. Talent: 3rd-hit True burst (180% ATK). S3: ATK+150%/block=3/30s."""
    op = _base_stats()
    op.name = "Qiubai"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = CENTURION_RANGE
    op.block = 2
    op.cost = 20
    op.talents = [TalentComponent(name="Feathered Gale", behavior_tag=_SEAL_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Wind Slash",
            slot="S2",
            sp_cost=30,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Soulwind",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
