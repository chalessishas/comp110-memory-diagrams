"""Liskarm — 5* Defender (Sentinel archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent: Lightning Discharge — when hit, deal 120% ATK as Arts to attacker (E2 rank).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.liskarm import make_liskarm as _base_stats


DEFENDER_MELEE_1 = RangeShape(tiles=((0, 0),))

_LIGHTNING_TAG = "liskarm_lightning_discharge"
_LIGHTNING_RATIO = 1.20   # 120% ATK at E2


def _on_hit_received(world, defender: UnitState, attacker, damage: int) -> None:
    arc_dmg = attacker.take_arts(int(defender.effective_atk * _LIGHTNING_RATIO))
    world.global_state.total_damage_dealt += arc_dmg
    world.log(f"⚡ Liskarm arc → {attacker.name}  dmg={arc_dmg}  ({attacker.hp}/{attacker.max_hp})")


register_talent(_LIGHTNING_TAG, on_hit_received=_on_hit_received)


def make_liskarm() -> UnitState:
    """Liskarm E2 max, trust 100. Base stats from akgd; Lightning Discharge talent wired."""
    op = _base_stats()
    op.name = "Liskarm"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.range_shape = DEFENDER_MELEE_1
    op.cost = 21
    op.talents = [TalentComponent(name="Lightning Discharge", behavior_tag=_LIGHTNING_TAG)]
    return op
