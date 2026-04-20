"""Liskarm — 5* Defender (Sentinel archetype).

Base stats from ArknightsGameData (E2 max, trust 100, char_107_liskam).
  HP=3240, ATK=470, DEF=755, RES=0, atk_interval=1.2s, cost=21, block=3.

Talent "Lightning Discharge" (E2):
  When Liskarm takes damage:
    1. Deals 120% ATK as Arts to the attacker.
    2. Gives +1 SP to Liskarm herself (if her skill has room).
    3. Gives +1 SP to one random deployed nearby ally (within _SP_RADIUS tiles)
       whose skill has SP room.
  During S3: gives +1 SP to ALL nearby allies in radius (not random one).

S1 "Overcharge": DEF +50%, duration=35s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "Energies Converging": ATK+100%, DEF+60%, 30s MANUAL.
  Lightning Discharge upgrades to give SP to ALL nearby allies.
  sp_cost=50, initial_sp=15, AUTO_TIME.
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

# --- S3: Energies Converging ---
_S3_TAG = "liskarm_s3_energies_converging"
_S3_ATK_RATIO = 1.00      # ATK +100%
_S3_DEF_RATIO = 0.60      # DEF +60%
_S3_ATK_BUFF_TAG = "liskarm_s3_atk"
_S3_DEF_BUFF_TAG = "liskarm_s3_def"
_S3_DURATION = 30.0
_S3_ACTIVE_ATTR = "_liskarm_s3_active"


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
    if getattr(defender, _S3_ACTIVE_ATTR, False):
        # S3 active: give SP to ALL nearby allies
        for ally in candidates:
            _grant_sp(ally, _SP_PER_HIT)
            world.log(f"⚡ Liskarm S3 SP battery ALL → {ally.name}  sp={ally.skill.sp:.1f}/{ally.skill.sp_cost}")
    elif candidates:
        chosen = world.rng.choice(candidates)
        _grant_sp(chosen, _SP_PER_HIT)
        world.log(f"⚡ Liskarm SP battery → {chosen.name}  sp={chosen.skill.sp:.1f}/{chosen.skill.sp_cost}")


register_talent(_LIGHTNING_TAG, on_hit_received=_on_hit_received)


# --- S3: Energies Converging ---
def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S3_DEF_RATIO, source_tag=_S3_DEF_BUFF_TAG,
    ))
    setattr(carrier, _S3_ACTIVE_ATTR, True)
    world.log(f"Liskarm S3 Energies Converging — ATK+{_S3_ATK_RATIO:.0%}, DEF+{_S3_DEF_RATIO:.0%}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG)]
    setattr(carrier, _S3_ACTIVE_ATTR, False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# --- S2: Voltaic Shield ---
_S2_TAG = "liskarm_s2_voltaic_shield"
_S2_DEF_RATIO = 0.80         # DEF +80% while active
_S2_PULSE_DPS = 1.50         # 150% ATK Arts damage per second in pulse radius
_S2_PULSE_RADIUS = 1.5       # tile radius of electric pulse
_S2_PULSE_INTERVAL = 1.0     # pulse fires every 1 second
_S2_SOURCE_TAG = "liskarm_s2_voltaic"
_S2_ACCUM_ATTR = "_liskarm_s2_pulse_accum"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    setattr(carrier, _S2_ACCUM_ATTR, 0.0)
    world.log(f"Liskarm S2 Voltaic Shield — DEF+{_S2_DEF_RATIO:.0%}, pulse r={_S2_PULSE_RADIUS}")


def _s2_on_tick(world, carrier: UnitState, dt: float) -> None:
    if carrier.position is None:
        return
    accum = getattr(carrier, _S2_ACCUM_ATTR, 0.0) + dt
    pulses = int(accum / _S2_PULSE_INTERVAL)
    if pulses > 0:
        cx, cy = carrier.position
        raw = int(carrier.effective_atk * _S2_PULSE_DPS * _S2_PULSE_INTERVAL)
        for e in world.enemies():
            if not e.alive or e.position is None:
                continue
            dist = sqrt((e.position[0] - cx) ** 2 + (e.position[1] - cy) ** 2)
            if dist <= _S2_PULSE_RADIUS:
                for _ in range(pulses):
                    dealt = e.take_arts(raw)
                    world.global_state.total_damage_dealt += dealt
                world.log(f"⚡ Liskarm S2 pulse ×{pulses} → {e.name}  dmg={raw * pulses}")
    setattr(carrier, _S2_ACCUM_ATTR, accum - pulses * _S2_PULSE_INTERVAL)


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


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
    """Liskarm E2 max. Lightning Discharge talent + S1/S2/S3."""
    op = _base_stats()
    op.name = "Liskarm"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.range_shape = DEFENDER_MELEE_1
    op.cost = 21
    op.talents = [TalentComponent(name="Lightning Discharge", behavior_tag=_LIGHTNING_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Energies Converging",
            slot="S3",
            sp_cost=50,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Voltaic Shield",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=20.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S1":
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
