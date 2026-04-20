"""Shining (闪灵) — 6* Medic (Single-target archetype).

Talent "Illuminate" (E2): When Shining heals an ally, that ally gains a physical
  SHIELD worth 15% of Shining's ATK for 10s. Existing shields from same source
  are refreshed (amount and timer reset, not stacked).

S2 "Faith": Immediately applies a SHIELD worth 300% ATK to the most-injured ally.
  Duration: 30s. No active heal during skill (passive heals continue). sp_cost=3.

S3 "Creed Field": 35s duration. ATK+50% to Shining. All allies within Shining's
  heal range receive +30 flat DEF aura (refreshed each tick).
  sp_cost=50, initial_sp=20, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype, SPGainMode, SkillTrigger, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.shining import make_shining as _base_stats


MEDIC_RANGE = RangeShape(tiles=((1, 0), (2, 0), (3, 0), (1, -1), (1, 1)))

# --- Talent: Illuminate ---
_ILLUMINATE_TAG = "shining_illuminate"
_ILLUMINATE_SHIELD_RATIO = 0.15  # 15% of Shining ATK
_ILLUMINATE_DURATION = 10.0
_ILLUMINATE_SOURCE = "shining_illuminate_shield"


def _illuminate_on_attack_hit(world, attacker, target, damage: int) -> None:
    if attacker.attack_type != AttackType.HEAL:
        return
    shield_amount = int(attacker.effective_atk * _ILLUMINATE_SHIELD_RATIO)
    target.statuses = [s for s in target.statuses if s.source_tag != _ILLUMINATE_SOURCE]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SHIELD,
        source_tag=_ILLUMINATE_SOURCE,
        expires_at=world.global_state.elapsed + _ILLUMINATE_DURATION,
        params={"amount": shield_amount},
    ))


register_talent(_ILLUMINATE_TAG, on_attack_hit=_illuminate_on_attack_hit)


# --- S2: Faith — instant SHIELD on most-injured ally ---
_S2_TAG = "shining_s2_faith"
_S2_SHIELD_RATIO = 3.0   # 300% ATK as shield
_S2_SHIELD_DURATION = 30.0
_S2_SOURCE = "shining_s2_shield"


def _s2_on_start(world, unit) -> None:
    if unit.position is None:
        return
    candidates = [u for u in world.allies() if u is not unit and u.alive and u.deployed]
    if not candidates:
        return
    target = min(candidates, key=lambda u: u.hp / max(u.max_hp, 1))
    shield_amount = int(unit.effective_atk * _S2_SHIELD_RATIO)
    target.statuses = [s for s in target.statuses if s.source_tag != _S2_SOURCE]
    target.statuses.append(StatusEffect(
        kind=StatusKind.SHIELD,
        source_tag=_S2_SOURCE,
        expires_at=world.global_state.elapsed + _S2_SHIELD_DURATION,
        params={"amount": shield_amount},
    ))
    world.log(f"Shining S2 → {target.name}  shield={shield_amount}")


register_skill(_S2_TAG, on_start=_s2_on_start)


# --- S3: Creed Field — ATK+50% + DEF aura to allies in range ---
_S3_TAG = "shining_s3_creed_field"
_S3_ATK_RATIO = 0.50          # ATK +50% to Shining
_S3_ATK_BUFF_TAG = "shining_s3_atk"
_S3_DEF_FLAT = 30             # +30 DEF to in-range allies
_S3_DEF_BUFF_TAG = "shining_s3_def_aura"
_S3_DEF_BUFF_TTL = 0.3
_S3_DURATION = 35.0


def _in_range(carrier: UnitState, ally: UnitState) -> bool:
    if carrier.position is None or ally.position is None:
        return False
    ox, oy = carrier.position
    ax, ay = ally.position
    return (round(ax) - round(ox), round(ay) - round(oy)) in set(carrier.range_shape.tiles)


def _s3_stamp_def_aura(world, carrier: UnitState) -> None:
    now = world.global_state.elapsed
    new_expires = now + _S3_DEF_BUFF_TTL + 0.15
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed:
            continue
        if not _in_range(carrier, ally):
            continue
        existing = next((b for b in ally.buffs if b.source_tag == _S3_DEF_BUFF_TAG), None)
        if existing is not None:
            existing.expires_at = new_expires
        else:
            ally.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.FLAT,
                value=_S3_DEF_FLAT, source_tag=_S3_DEF_BUFF_TAG,
                expires_at=new_expires,
            ))


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    _s3_stamp_def_aura(world, carrier)
    world.log(f"Shining S3 Creed Field — ATK+{_S3_ATK_RATIO:.0%} DEF+{_S3_DEF_FLAT} aura/{_S3_DURATION}s")


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    _s3_stamp_def_aura(world, carrier)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_DEF_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_shining(slot: str = "S2") -> UnitState:
    """Shining E2 max. Talent Illuminate: heal→shield 15% ATK/10s. S2: 300% ATK shield."""
    op = _base_stats()
    op.name = "Shining"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 20
    op.talents = [TalentComponent(name="Illuminate", behavior_tag=_ILLUMINATE_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Faith",
            slot="S2",
            sp_cost=3,
            initial_sp=0,
            duration=0.0,   # instant effect
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Creed Field",
            slot="S3",
            sp_cost=50,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
