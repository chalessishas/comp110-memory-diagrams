"""Firewatch (天火) — 5* Sniper (Anti-Air archetype).

Anti-Air Sniper trait: prioritizes AIRBORNE enemies over ground enemies.
  Implemented in targeting_system via SNIPER_ANTI_AIR archetype branch.

Talent "First Target" (E2): When attacking an AIRBORNE enemy, ATK +30%.
  Implemented as a short-lived buff refreshed each tick while current target is aerial.

S2 "Flash Arrow" (M3): ATK +60%, 15s; each hit stuns AIRBORNE targets for 1s.
  sp_cost=18, initial_sp=10, AUTO_ATTACK gain.

Base stats from ArknightsGameData (E2 max, trust 100, char_166_skfire).
  HP=1620, ATK=874, DEF=142, RES=0, atk_interval=1.05s, cost=13, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Mobility, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.skfire import make_skfire as _base_stats


ANTI_AIR_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: First Target ---
_TALENT_TAG = "firewatch_first_target"
_FIRST_TARGET_RATIO = 0.30
_FIRST_TARGET_BUFF_TAG = "firewatch_first_target_buff"
_BUFF_WINDOW = 0.2   # short-lived; refreshed each tick while targeting aerial

# --- S2: Flash Arrow ---
_S2_TAG = "firewatch_s2_flash_arrow"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "firewatch_s2_atk"
_S2_DURATION = 15.0
_S2_STUN_DURATION = 1.0
_S2_STUN_TAG = "firewatch_s2_stun"


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    target = getattr(carrier, "__target__", None)
    elapsed = world.global_state.elapsed
    if target is not None and target.alive and target.mobility == Mobility.AIRBORNE:
        # Refresh short-lived ATK buff while targeting aerial enemy
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _FIRST_TARGET_BUFF_TAG]
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK,
            stack=BuffStack.RATIO,
            value=_FIRST_TARGET_RATIO,
            source_tag=_FIRST_TARGET_BUFF_TAG,
            expires_at=elapsed + _BUFF_WINDOW,
        ))
    # If not targeting aerial, buff naturally expires


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    # S2 Flash Arrow: stun aerial targets when skill is active
    sk = attacker.skill
    if sk is None or sk.active_remaining <= 0:
        return
    if target.mobility != Mobility.AIRBORNE:
        return
    elapsed = world.global_state.elapsed
    target.statuses = [s for s in target.statuses if s.source_tag != _S2_STUN_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.STUN,
        source_tag=_S2_STUN_TAG,
        expires_at=elapsed + _S2_STUN_DURATION,
    ))
    world.log(f"Firewatch S2 stuns {target.name} ({_S2_STUN_DURATION}s)")


register_talent(_TALENT_TAG, on_tick=_talent_on_tick, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_firewatch(slot: str = "S2") -> UnitState:
    """Firewatch E2 max. Anti-Air: prioritizes aerial targets. Talent: ATK+30% vs aerial."""
    op = _base_stats()
    op.name = "Firewatch"
    op.archetype = RoleArchetype.SNIPER_ANTI_AIR
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = False
    op.range_shape = ANTI_AIR_RANGE
    op.block = 1
    op.cost = 13

    op.talents = [TalentComponent(name="First Target", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Flash Arrow",
            slot="S2",
            sp_cost=18,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
