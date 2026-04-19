"""Ch'en — 6* Guard (Lord archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Sheathed Strike": MANUAL instant — deals 380% ATK arts damage to all enemies in range.
sp_cost=20, initial_sp=10.
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill, manual_trigger
from data.characters.generated.chen import make_chen as _base_stats


LORD_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

_S2_TAG = "chen_s2_sheathed_strike"
_S2_ATK_MULTIPLIER = 3.80   # 380% ATK at M3


def _s2_on_start(world, carrier: UnitState) -> None:
    """Instant arts burst to all enemies in range."""
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
            f"Ch'en S2 → {enemy.name}  dmg={dealt}  ({enemy.hp}/{enemy.max_hp})"
        )


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_chen(slot: str = "S2") -> UnitState:
    """Ch'en E2 max, trust 100. S2 Sheathed Strike wired (MANUAL)."""
    op = _base_stats()
    op.name = "Ch'en"
    op.archetype = RoleArchetype.GUARD_LORD
    op.range_shape = LORD_RANGE
    op.cost = 23
    if slot == "S2":
        op.skill = SkillComponent(
            name="Sheathed Strike",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=0.0,   # instant
            sp_gain_mode=SPGainMode.AUTO_ATTACK,   # charges on hit
            trigger=SkillTrigger.MANUAL,
            behavior_tag=_S2_TAG,
        )
    return op
