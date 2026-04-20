"""Liskarm — 5* Defender (Sentinel archetype).

Base stats from ArknightsGameData (E2 max, trust 100, char_107_liskam).
  HP=3240, ATK=470, DEF=755, RES=0, atk_interval=1.2s, cost=21, block=3.

Talent "Lightning Discharge" (E2):
  When Liskarm takes damage:
    1. Deals 120% ATK as Arts to the attacker.
    2. Gives +1 SP to Liskarm herself (if her skill has room).
    3. Gives +1 SP to one random deployed nearby ally (within _SP_RADIUS tiles)
       whose skill has SP room.

S1 "Overcharge": DEF +50%, duration=35s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.
"""
from __future__ import annotations
import random
from math import sqrt
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype, SPGainMode,
    SkillTrigger,
)
from core.systems.skill_system import register_skill
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


# --- S1: Overcharge ---
_S1_TAG = "liskarm_s1_overcharge"
_S1_DEF_RATIO = 0.50     # DEF +50%
_S1_SOURCE_TAG = "liskarm_s1_overcharge"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_SOURCE_TAG,
    ))
    world.log(f"Liskarm S1 Overcharge — DEF +{_S1_DEF_RATIO:.0%}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_SOURCE_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_liskarm(slot: str = "S1") -> UnitState:
    """Liskarm E2 max. Lightning Discharge talent + S1 Overcharge: DEF+50% 35s."""
    op = _base_stats()
    op.name = "Liskarm"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.range_shape = DEFENDER_MELEE_1
    op.cost = 21
    op.talents = [TalentComponent(name="Lightning Discharge", behavior_tag=_LIGHTNING_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Overcharge",
            slot="S1",
            sp_cost=25,
            initial_sp=10,
            duration=35.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
