"""Blemishine (瑕光) — 6★ Defender (Protector archetype).

DEF_PROTECTOR trait: When blocking enemies equal to block capacity, gains a
  _TRAIT_DEF_BONUS ratio bonus to DEF (implemented via on_tick conditional buff).

Talent "Aegis" (E2):
  When blocking at full capacity AND HP > 50%, grant _TALENT_DEF_BONUS additional
  DEF ratio. Both trait and talent stack to reward staying at full engagement.

S2 "Iron Aegis": MANUAL.
  ATK +_S2_ATK_RATIO, DEF +_S2_DEF_RATIO for _S2_DURATION seconds.
  sp_cost=45, initial_sp=25, AUTO_TIME, MANUAL trigger.

S3 "Holy Flash": MANUAL.
  ATK +300%, converts attacks to True damage (bypasses DEF/RES).
  After each attack, heals all allies within 1 tile for 100% of ATK.
  sp_cost=35, initial_sp=15, AUTO_TIME, 15s duration.

Base stats from ArknightsGameData (E2 max, trust 100, char_423_blemsh):
  HP=3242, ATK=581, DEF=601, RES=10, atk_interval=1.2s, cost=22, block=3.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.blemsh import make_blemsh as _base_stats


PROTECTOR_RANGE = RangeShape(tiles=((0, 0),))

_TALENT_TAG = "blemsh_aegis"
_TRAIT_DEF_BONUS = 0.50         # +50% DEF when blocking at capacity (trait)
_TALENT_DEF_BONUS = 0.30        # +30% more DEF when HP > 50% AND at capacity (talent)
_TRAIT_DEF_TAG = "blemsh_trait_def"
_TALENT_DEF_TAG = "blemsh_talent_def"

_S2_TAG = "blemsh_s2_iron_aegis"
_S2_ATK_RATIO = 0.40
_S2_DEF_RATIO = 0.60
_S2_ATK_BUFF_TAG = "blemsh_s2_atk"
_S2_DEF_BUFF_TAG = "blemsh_s2_def"
_S2_DURATION = 25.0

_S3_TAG = "blemsh_s3_holy_flash"
_S3_ATK_RATIO = 3.00        # ATK +300%
_S3_BUFF_TAG = "blemsh_s3_atk"
_S3_HEAL_RATIO = 1.00       # heal 100% ATK to allies within 1 tile after each attack
_S3_DURATION = 15.0
_S3_ACTIVE_ATTR = "_blemsh_s3_active"   # instance attr — avoids module-level set cross-test leak


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    blocking = sum(1 for e in world.enemies() if carrier.unit_id in e.blocked_by_unit_ids)
    at_capacity = (blocking >= carrier.block)

    # --- Trait: DEF bonus at full block ---
    has_trait = any(b.source_tag == _TRAIT_DEF_TAG for b in carrier.buffs)
    if at_capacity and not has_trait:
        carrier.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=_TRAIT_DEF_BONUS, source_tag=_TRAIT_DEF_TAG,
        ))
    elif not at_capacity and has_trait:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TRAIT_DEF_TAG]

    # --- Talent: extra DEF when HP > 50% AND at capacity ---
    hp_above_half = (carrier.hp > carrier.max_hp * 0.5)
    has_talent = any(b.source_tag == _TALENT_DEF_TAG for b in carrier.buffs)
    talent_active = at_capacity and hp_above_half
    if talent_active and not has_talent:
        carrier.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=_TALENT_DEF_BONUS, source_tag=_TALENT_DEF_TAG,
        ))
    elif not talent_active and has_talent:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_DEF_TAG]


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if not getattr(attacker, _S3_ACTIVE_ATTR, False) or attacker.position is None:
        return
    heal_amount = int(attacker.effective_atk * _S3_HEAL_RATIO)
    ax, ay = attacker.position
    for ally in world.units:
        if not ally.alive or ally.faction != Faction.ALLY:
            continue
        if ally.position is None:
            continue
        ox, oy = ally.position
        if max(abs(ox - ax), abs(oy - ay)) <= 1:   # Chebyshev distance ≤ 1 (8-tile Moore neighborhood)
            actual = ally.heal(heal_amount)
            world.global_state.total_healing_done += actual
            world.log(f"Blemishine Holy Flash heal → {ally.name} +{actual}")


register_talent(_TALENT_TAG, on_tick=_talent_on_tick, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    carrier._blemsh_original_attack_type = carrier.attack_type
    carrier.attack_type = AttackType.TRUE
    setattr(carrier, _S3_ACTIVE_ATTR, True)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]
    carrier.attack_type = getattr(carrier, "_blemsh_original_attack_type", AttackType.PHYSICAL)
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_blemishine(slot: str = "S2") -> UnitState:
    """Blemishine E2 max. Trait+Talent: DEF bonus when fully blocking. S2: ATK+DEF burst. S3: True dmg + heal."""
    op = _base_stats()
    op.name = "Blemishine"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = PROTECTOR_RANGE
    op.block = 3
    op.cost = 22

    op.talents = [TalentComponent(name="Aegis", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Iron Aegis",
            slot="S2",
            sp_cost=45,
            initial_sp=25,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Holy Flash",
            slot="S3",
            sp_cost=35,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
