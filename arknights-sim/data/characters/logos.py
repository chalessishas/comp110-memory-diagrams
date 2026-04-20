"""Logos (逻各斯) — 6★ Caster (Charge archetype).

Arts attacker. Unique talent: gains ATK buff after deployment stabilization.

Talent "Stable Hypothesis" (E2):
  After being deployed for _TALENT_DELAY seconds, ATK +25%.
  Once applied, the buff persists for the rest of the deployment.
  Implemented via on_tick: single-fire buff, never removed while deployed.

S2 "Theorem Derivation": ATK +60% for 20s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger.

S3 "Absolute Logos": ATK +80% for 30s, wide-range arts barrage.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_4133_logos):
  HP=1663, ATK=761, DEF=119, RES=20, atk_interval=1.6s, cost=21, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.logos import make_logos as _base_stats


CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Stable Hypothesis ---
_TALENT_TAG = "logos_stable_hypothesis"
_TALENT_DELAY = 10.0      # seconds after deploy before buff activates
_TALENT_ATK_RATIO = 0.25  # +25% ATK
_TALENT_BUFF_TAG = "logos_talent_atk"

# --- S2: Theorem Derivation ---
_S2_TAG = "logos_s2_theorem_derivation"
_S2_ATK_RATIO = 0.60
_S2_BUFF_TAG = "logos_s2_atk"
_S2_DURATION = 20.0

# --- S3: Absolute Logos ---
_S3_TAG = "logos_s3_absolute_logos"
_S3_ATK_RATIO = 0.80
_S3_BUFF_TAG = "logos_s3_atk"
_S3_DURATION = 30.0


# ---------------------------------------------------------------------------
# Talent: Stable Hypothesis — deploy-time-gated ATK buff
# ---------------------------------------------------------------------------

def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.deploy_time < 0:
        return
    if any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs):
        return  # already active, nothing to do
    elapsed = world.global_state.elapsed - carrier.deploy_time
    if elapsed >= _TALENT_DELAY:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
        ))
        world.log(f"Logos Stable Hypothesis: ATK+{_TALENT_ATK_RATIO:.0%} activated "
                  f"({elapsed:.1f}s since deploy)")


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


# ---------------------------------------------------------------------------
# S2: Theorem Derivation
# ---------------------------------------------------------------------------

def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Logos S2 Theorem Derivation — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# ---------------------------------------------------------------------------
# S3: Absolute Logos
# ---------------------------------------------------------------------------

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Logos S3 Absolute Logos — ATK+{_S3_ATK_RATIO:.0%}/{_S3_DURATION}s")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_logos(slot: str = "S3") -> UnitState:
    """Logos E2 max. Stable Hypothesis: ATK +25% after 10s deployed. S2/S3 ATK buffs."""
    op = _base_stats()
    op.name = "Logos"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = CASTER_RANGE
    op.block = 1
    op.cost = 21

    op.talents = [TalentComponent(name="Stable Hypothesis", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Theorem Derivation",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Absolute Logos",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
