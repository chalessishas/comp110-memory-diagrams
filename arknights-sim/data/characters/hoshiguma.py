"""Hoshiguma — 6* Defender (Juggernaut archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "Overweight": when HP > 50%, reduce damage taken by 20% (E2 rank).
Skill S2 "Unshakeable" (rank VII, E2):
  DEF +300 for 20s. AUTO_TIME, AUTO trigger. sp_cost=40.
  Classic Liskarm synergy target: Liskarm's SP battery charges this skill.

S3 "Shield Bash": 25s, MANUAL.
  ATK +100%, DEF +200. While active: each hit received triggers a counter-attack
  dealing 100% ATK physical damage to every enemy currently blocking Hoshiguma.
  sp_cost=60, initial_sp=20, AUTO_TIME.
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.hoshiguma import make_hoshiguma as _base_stats


DEFENDER_MELEE_BLOCK3 = RangeShape(tiles=((0, 0),))

_OVERWEIGHT_TAG = "hoshiguma_overweight"

_S2_TAG = "hoshiguma_s2_unshakeable"
_S2_DEF_TAG = "hoshiguma_s2_def"
_S2_DEF_FLAT = 300   # rank VII approximate (+300 DEF for 20s)

# --- S3: Shield Bash ---
_S3_TAG = "hoshiguma_s3_shield_bash"
_S3_ATK_RATIO = 1.00        # ATK +100%
_S3_DEF_FLAT = 200          # DEF +200
_S3_ATK_BUFF_TAG = "hoshiguma_s3_atk"
_S3_DEF_BUFF_TAG = "hoshiguma_s3_def"
_S3_COUNTER_RATIO = 1.00    # 100% ATK physical counter per hit received
_S3_ACTIVE_ATTR = "_hoshi_s3_active"
_S3_DURATION = 25.0


def _overweight_on_hit_received(world, defender: UnitState, attacker: UnitState, damage: int) -> None:
    if not getattr(defender, _S3_ACTIVE_ATTR, False):
        return
    raw = int(floor(defender.effective_atk * _S3_COUNTER_RATIO))
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed:
            continue
        if defender.unit_id not in enemy.blocked_by_unit_ids:
            continue
        dealt = enemy.take_physical(raw)
        world.global_state.total_damage_dealt += dealt
        world.log(f"Hoshiguma S3 counter → {enemy.name}  dmg={dealt}")


register_talent(_OVERWEIGHT_TAG, on_hit_received=_overweight_on_hit_received)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_S2_DEF_FLAT, source_tag=_S2_DEF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_S3_DEF_FLAT, source_tag=_S3_DEF_BUFF_TAG,
    ))
    setattr(carrier, _S3_ACTIVE_ATTR, True)
    world.log(f"Hoshiguma S3 Shield Bash — ATK+{_S3_ATK_RATIO:.0%}, DEF+{_S3_DEF_FLAT}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [
        b for b in carrier.buffs
        if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG)
    ]
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_hoshiguma(slot: str = "S2") -> UnitState:
    """Hoshiguma E2 max, trust 100. Overweight talent + S2 Unshakeable / S3 Shield Bash."""
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
    if slot == "S2":
        op.skill = SkillComponent(
            name="Unshakeable", slot="S2",
            sp_cost=40, initial_sp=0, duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = 0.0
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Shield Bash", slot="S3",
            sp_cost=60, initial_sp=20, duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
