"""Ifrit — 6* Caster (Core Caster archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Combustion": Instant AOE arts burst — deals 260% ATK arts damage to all enemies in range.
sp_cost=22, initial_sp=10.
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent, Buff
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ifrit import make_ifrit as _base_stats


# --- Talent: Injection ---
_INJECTION_TAG = "ifrit_injection"
_INJECTION_BUFF_TAG = "ifrit_injection_def"
_DEF_REDUCTION = 0.15    # -15% DEF (E2 max)
_INJECTION_DURATION = 10.0


def _injection_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    now = world.global_state.elapsed
    new_expires = now + _INJECTION_DURATION
    existing = next((b for b in target.buffs if b.source_tag == _INJECTION_BUFF_TAG), None)
    if existing is not None:
        existing.expires_at = new_expires
    else:
        target.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=-_DEF_REDUCTION, source_tag=_INJECTION_BUFF_TAG,
            expires_at=new_expires,
        ))


register_talent(_INJECTION_TAG, on_attack_hit=_injection_on_attack_hit)


# Ifrit fires straight ahead in a 1×5 line (standard Core Caster range)
CORE_CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, 1), (2, 1),
    (1, -1), (2, -1),
))

_S2_TAG = "ifrit_s2_combustion"
_S2_ATK_MULTIPLIER = 2.60   # 260% ATK at rank 7


def _s2_on_start(world, carrier: UnitState) -> None:
    """Instant AOE: deal 260% ATK arts damage to all enemies in range."""
    if carrier.position is None:
        return
    ox, oy = carrier.position
    tiles = set(carrier.range_shape.tiles)
    burst_atk = int(floor(carrier.effective_atk * _S2_ATK_MULTIPLIER))
    for enemy in world.enemies():
        if not enemy.alive or enemy.position is None:
            continue
        dx = round(enemy.position[0]) - round(ox)
        dy = round(enemy.position[1]) - round(oy)
        if (dx, dy) not in tiles:
            continue
        dealt = enemy.take_arts(burst_atk)
        world.global_state.total_damage_dealt += dealt
        world.log(
            f"Ifrit S2 burst → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})"
        )


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_ifrit(slot: str = "S2") -> UnitState:
    """Ifrit E2 max, trust 100. S2 Combustion wired."""
    op = _base_stats()
    op.name = "Ifrit"
    op.archetype = RoleArchetype.CASTER_CORE
    op.range_shape = CORE_CASTER_RANGE
    op.cost = 34
    op.talents = [TalentComponent(name="Injection", behavior_tag=_INJECTION_TAG)]
    if slot == "S2":
        op.skill = SkillComponent(
            name="Combustion",
            slot="S2",
            sp_cost=22,
            initial_sp=10,
            duration=0.0,   # instant — fires once and SP resets
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
            requires_target=True,
        )
    return op
