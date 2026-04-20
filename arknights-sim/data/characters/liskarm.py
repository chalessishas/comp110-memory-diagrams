"""Liskarm — 5* Defender (Sentinel archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "Lightning Discharge" (E2):
  When Liskarm takes damage:
    1. Deals 120% ATK as Arts to the attacker.
    2. Gives +1 SP to Liskarm herself (if her skill has room).
    3. Gives +1 SP to one random deployed nearby ally (within _SP_RADIUS tiles)
       whose skill has SP room.

The SP-battery mechanic makes Liskarm a support defender who fuels adjacent
operators (e.g. Hoshiguma S2) while tanking hits.

Constants (E2 rank, verified vs arknights.wiki.gg/wiki/Liskarm):
  Arc ratio: 120% ATK Arts damage.
  SP per hit: +1 to self, +1 to random nearby ally.
  SP radius: ~1.5 tiles (covers all 8 adjacent cells).
"""
from __future__ import annotations
import random
from math import sqrt
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype, SPGainMode,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.liskarm import make_liskarm as _base_stats


DEFENDER_MELEE_1 = RangeShape(tiles=((0, 0),))

_LIGHTNING_TAG = "liskarm_lightning_discharge"
_LIGHTNING_RATIO = 1.20   # 120% ATK at E2
_SP_PER_HIT = 1.0         # SP gained by self and one ally on each hit received
_SP_RADIUS = 1.5          # tile radius for ally SP battery (covers all 8 adjacent)


def _grant_sp(unit: UnitState, amount: float) -> bool:
    """Give SP to unit if its skill has room. Returns True if SP was actually granted."""
    sk = unit.skill
    if sk is None or sk.sp_gain_mode == SPGainMode.ON_DEPLOY:
        return False
    if sk.active_remaining > 0:
        return False   # skill already firing; SP not relevant
    if sk.sp >= sk.sp_cost:
        return False   # already full
    sk.sp = min(sk.sp + amount, float(sk.sp_cost))
    return True


def _on_hit_received(world, defender: UnitState, attacker, damage: int) -> None:
    # 1. Arc counter-damage
    arc_dmg = attacker.take_arts(int(defender.effective_atk * _LIGHTNING_RATIO))
    world.global_state.total_damage_dealt += arc_dmg
    world.log(f"⚡ Liskarm arc → {attacker.name}  dmg={arc_dmg}  ({attacker.hp}/{attacker.max_hp})")

    # 2. +1 SP to self
    _grant_sp(defender, _SP_PER_HIT)

    # 3. +1 SP to one random nearby ally with skill room
    if defender.position is None:
        return
    dx, dy = defender.position
    candidates = [
        u for u in world.allies()
        if u is not defender
        and u.deployed
        and u.alive
        and u.position is not None
        and sqrt((u.position[0] - dx) ** 2 + (u.position[1] - dy) ** 2) <= _SP_RADIUS
        and u.skill is not None
        and u.skill.sp < u.skill.sp_cost
        and u.skill.active_remaining == 0.0
    ]
    if candidates:
        chosen = world.rng.choice(candidates)
        _grant_sp(chosen, _SP_PER_HIT)
        world.log(f"⚡ Liskarm SP battery → {chosen.name}  sp={chosen.skill.sp:.1f}/{chosen.skill.sp_cost}")


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
