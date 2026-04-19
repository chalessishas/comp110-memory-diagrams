"""Nearl (临光) — 6* Defender (Knight archetype).

Talent "Holy Knight's Light": Every 25 seconds, restores HP equal to 8% of max_hp
  to all allies within range (5-tile cross). Passive, fires via on_tick accumulator.

S2 "Justice" (optional, not implemented here): ATK buff + slight DEF buff, instant.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.nearl import make_nearl as _base_stats


DEFENDER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "nearl_holy_knight_light"
_HEAL_INTERVAL = 25.0    # seconds between each AoE heal pulse
_HEAL_RATIO = 0.08       # 8% of ally max_hp restored per pulse
_ACCUM_ATTR = "_nearl_heal_accum"

# Heal range: 5-tile cross (own tile + 4 orthogonal)
_HEAL_RANGE = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}


def _on_tick(world, carrier: UnitState, dt: float) -> None:
    """Accumulate time; when threshold reached, heal all allies in range."""
    accum = getattr(carrier, _ACCUM_ATTR, 0.0) + dt
    if accum < _HEAL_INTERVAL:
        setattr(carrier, _ACCUM_ATTR, accum)
        return

    # Heal pulse
    if carrier.position is not None:
        cx, cy = round(carrier.position[0]), round(carrier.position[1])
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp or ally.position is None:
                continue
            ax, ay = round(ally.position[0]), round(ally.position[1])
            if (ax - cx, ay - cy) in _HEAL_RANGE:
                healed = ally.heal(int(ally.max_hp * _HEAL_RATIO))
                if healed > 0:
                    world.global_state.total_healing_done += healed
                    world.log(
                        f"Nearl Holy Knight → {ally.name}  heal={healed}  ({ally.hp}/{ally.max_hp})"
                    )

    setattr(carrier, _ACCUM_ATTR, accum - _HEAL_INTERVAL)


register_talent(_TALENT_TAG, on_tick=_on_tick)


def make_nearl() -> UnitState:
    """Nearl E2 max. Talent: passive AoE HP restore every 25s."""
    op = _base_stats()
    op.name = "Nearl"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_RANGE
    op.cost = 21

    op.talents = [TalentComponent(name="Holy Knight's Light", behavior_tag=_TALENT_TAG)]
    return op
