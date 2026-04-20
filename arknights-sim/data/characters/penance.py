"""Penance (贝娜) — 6* Guard (Dreadnought archetype).

Talent "Blood Weaving":
  - When an enemy within Penance's range is killed, she gains +_SHIELD_PER_KILL shield HP
    (stacked into a single SHIELD StatusEffect, capped at _MAX_SHIELD).
  - When Penance receives a hit, she deals _COUNTER_RATIO × ATK as Arts damage back to
    the attacker (counter-strike fires even while skill is active).

S2 "Verdict": ATK +60% for 35s (sp_cost=25, AUTO trigger, requires_target=True).
S3 "Purgation": ATK +100%, attacks deal Arts damage, counter-strike ratio ×0.65 ATK.
  Duration 40s, MANUAL. sp_cost=40, initial_sp=20, AUTO_ATTACK SP gain.
"""
from __future__ import annotations

from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent, register_enemy_killed_watcher
from data.characters.generated.bena import make_bena as _base_stats


PENANCE_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "penance_blood_weaving"
_SHIELD_PER_KILL = 500
_MAX_SHIELD = 2500
_SHIELD_TAG = "penance_blood_weaving_shield"

_COUNTER_RATIO = 0.35

_S2_TAG = "penance_s2_verdict"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "penance_s2_atk"

_S3_TAG = "penance_s3_purgation"
_S3_ATK_RATIO = 1.00          # ATK +100%
_S3_DURATION = 40.0
_S3_ATK_BUFF_TAG = "penance_s3_atk"
_S3_COUNTER_RATIO = 0.65      # enhanced counter-strike during S3 (vs 0.35 base)


def _on_hit_received(world, carrier: UnitState, attacker, damage: int) -> None:
    """Counter-strike: reflect Arts damage to the attacker."""
    if attacker is None:
        return
    ratio = _S3_COUNTER_RATIO if getattr(carrier, "_penance_s3_active", False) else _COUNTER_RATIO
    arts_dmg = attacker.take_arts(int(carrier.effective_atk * ratio))
    world.global_state.total_damage_dealt += arts_dmg
    world.log(f"Penance counter → {attacker.name}  arts={arts_dmg}")


def _on_enemy_killed(world, carrier: UnitState, killed) -> None:
    """Enemy dies in Penance's range → grow the blood-weaving shield pool."""
    if carrier.position is None or killed.position is None:
        return
    cx, cy = carrier.position
    kx, ky = killed.position
    if (round(kx) - round(cx), round(ky) - round(cy)) not in set(carrier.range_shape.tiles):
        return
    existing = next((s for s in carrier.statuses if s.source_tag == _SHIELD_TAG), None)
    if existing is not None:
        existing.params["amount"] = min(
            existing.params["amount"] + _SHIELD_PER_KILL, _MAX_SHIELD
        )
    else:
        carrier.statuses.append(StatusEffect(
            kind=StatusKind.SHIELD,
            source_tag=_SHIELD_TAG,
            expires_at=float("inf"),
            params={"amount": float(_SHIELD_PER_KILL)},
        ))
    world.log(f"Penance Blood Weaving: shield +{_SHIELD_PER_KILL}")


register_talent(_TALENT_TAG, on_hit_received=_on_hit_received)
register_enemy_killed_watcher(_TALENT_TAG, _on_enemy_killed)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier._penance_s3_active = True
    carrier._penance_original_attack_type = carrier.attack_type
    carrier.attack_type = AttackType.ARTS
    world.log(f"Penance S3 Purgation — ATK +{_S3_ATK_RATIO:.0%}, Arts mode, counter ×{_S3_COUNTER_RATIO}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    carrier._penance_s3_active = False
    carrier.attack_type = getattr(carrier, "_penance_original_attack_type", AttackType.PHYSICAL)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_penance(slot: str = "S2") -> UnitState:
    """Penance E2 max (overriding generated bena stats). Talent: Blood Weaving. S2: Verdict."""
    op = _base_stats()
    op.name = "Penance"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = PENANCE_RANGE
    op.block = 2
    op.cost = 17
    op.max_hp = 2886
    op.hp = 2886
    op.atk = 838
    op.defence = 570

    op.talents = [TalentComponent(name="Blood Weaving", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Verdict",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=35.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
            requires_target=True,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Purgation",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            behavior_tag=_S3_TAG,
            requires_target=True,
        )
    return op
