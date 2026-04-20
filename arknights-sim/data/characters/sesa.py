"""Sesa (慑砂) — 6★ Sniper (Heavy Shooter archetype).

SNIPER_HEAVY trait: Attacks slow the Movement Speed of enemies by 30% for 0.5s.

Talent "Percussion Resonance" (E2):
  Every _TALENT_HIT_COUNT attacks, fire an Arts explosion on the primary target dealing
  _TALENT_BONUS_ATK_RATIO × ATK Arts damage to all enemies within _TALENT_RADIUS tiles.

S2 "Drumroll": MANUAL.
  ATK +_S2_ATK_RATIO for _S2_DURATION seconds.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger.

S3 "Percussion Resonance II": ATK+120%, Percussion fires every 3 hits (down from 7).
  sp_cost=45, initial_sp=20, AUTO_TIME, MANUAL, 20s.

Base stats from ArknightsGameData (E2 max, trust 100, char_379_sesa):
  HP=1655, ATK=918, DEF=123, RES=0, atk_interval=2.8s, cost=28, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.sesa import make_sesa as _base_stats


HEAVY_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(1, 5) for dy in range(-1, 2)
))

_TRAIT_TAG = "sesa_trait_slow"
_TRAIT_SLOW_AMOUNT = 0.30
_TRAIT_SLOW_DURATION = 0.5

_TALENT_TAG = "sesa_percussion_resonance"
_TALENT_HIT_COUNT = 7
_TALENT_BONUS_ATK_RATIO = 1.5
_TALENT_RADIUS = 1.2

_S2_TAG = "sesa_s2_drumroll"
_S2_ATK_RATIO = 0.80
_S2_ATK_BUFF_TAG = "sesa_s2_atk"
_S2_DURATION = 20.0

_S3_TAG = "sesa_s3_percussion_resonance_ii"
_S3_ATK_RATIO = 1.20
_S3_ATK_BUFF_TAG = "sesa_s3_atk"
_S3_RESONANCE_INTERVAL = 3   # fires every 3 hits during S3 (vs 7 normally)
_S3_DURATION = 20.0
_S3_ACTIVE_ATTR = "_sesa_s3_active"


def _trait_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag=_TRAIT_TAG,
        expires_at=world.global_state.elapsed + _TRAIT_SLOW_DURATION,
        params={"amount": _TRAIT_SLOW_AMOUNT},
    ))


register_talent(_TRAIT_TAG, on_attack_hit=_trait_on_attack_hit)


def _percussion_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    if not hasattr(attacker, "_sesa_hit_count"):
        attacker._sesa_hit_count = 0
    attacker._sesa_hit_count += 1
    interval = _S3_RESONANCE_INTERVAL if getattr(attacker, _S3_ACTIVE_ATTR, False) else _TALENT_HIT_COUNT
    if attacker._sesa_hit_count % interval != 0:
        return
    if target.position is None:
        return
    raw_arts = int(attacker.effective_atk * _TALENT_BONUS_ATK_RATIO)
    tx, ty = target.position
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        ex, ey = e.position
        dist = ((ex - tx) ** 2 + (ey - ty) ** 2) ** 0.5
        if dist <= _TALENT_RADIUS:
            dealt = e.take_arts(raw_arts)
            world.global_state.total_damage_dealt += dealt
            world.log(f"Sesa Percussion Resonance → {e.name}  arts_dmg={dealt}")


register_talent(_TALENT_TAG, on_attack_hit=_percussion_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Percussion Resonance II ---
def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    setattr(carrier, _S3_ACTIVE_ATTR, True)
    world.log(f"Sesa S3 Percussion Resonance II — ATK+{_S3_ATK_RATIO:.0%}, resonance every {_S3_RESONANCE_INTERVAL} hits")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_sesa(slot: str = "S2") -> UnitState:
    """Sesa E2 max. SNIPER_HEAVY: SLOW on hit. Talent: Arts explosion every 7 hits. S2: ATK+80%."""
    op = _base_stats()
    op.name = "Sesa"
    op.archetype = RoleArchetype.SNIPER_HEAVY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = False
    op.range_shape = HEAVY_RANGE
    op.block = 1
    op.cost = 28

    op.talents = [
        TalentComponent(name="SNIPER_HEAVY Trait", behavior_tag=_TRAIT_TAG),
        TalentComponent(name="Percussion Resonance", behavior_tag=_TALENT_TAG),
    ]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Percussion Resonance II",
            slot="S3",
            sp_cost=45,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Drumroll",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
