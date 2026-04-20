"""Chyue (重岳) — 6★ Guard (Swordmaster archetype).

High-speed physical attacker, fastest attack interval among Guards (0.78s).

Talent "Stone Aegis" (E2):
  While SP ≥ _TALENT_SP_THRESHOLD, ATK +35%.
  Implemented via on_tick: buff applied when charged, removed when SP drops below
  threshold (skill activation, SP drain, etc.).

S2 "Boulder Cleave": ATK +80% for 20s.
  sp_cost=15, initial_sp=8, AUTO_ATTACK, AUTO trigger.

S3 "Colossus Strike": ATK +100% ammo-based (4 charges).
  Each attack consumes one charge; skill ends when all 4 are spent.
  sp_cost=30, initial_sp=15, AUTO_ATTACK, MANUAL trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_2024_chyue):
  HP=2635, ATK=650, DEF=393, RES=0, atk_interval=0.78s, cost=11, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.chyue import make_chyue as _base_stats


SWORDMASTER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Stone Aegis ---
_TALENT_TAG = "chyue_stone_aegis"
_TALENT_SP_THRESHOLD = 15.0    # SP must be ≥ this for the buff to activate
_TALENT_ATK_RATIO = 0.35       # +35% ATK when charged
_TALENT_BUFF_TAG = "chyue_talent_atk"

# --- S2: Boulder Cleave ---
_S2_TAG = "chyue_s2_boulder_cleave"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "chyue_s2_atk"
_S2_DURATION = 20.0

# --- S3: Colossus Strike ---
_S3_TAG = "chyue_s3_colossus_strike"
_S3_ATK_RATIO = 1.00           # +100% ATK per ammo hit
_S3_AMMO = 4
_S3_BUFF_TAG = "chyue_s3_atk"


# ---------------------------------------------------------------------------
# Talent: Stone Aegis — SP-threshold ATK buff
# ---------------------------------------------------------------------------

def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    sk = carrier.skill
    sp = sk.sp if sk is not None else 0.0
    # Buff inactive while skill is actively firing (sp reset to 0 on activation)
    above_threshold = sp >= _TALENT_SP_THRESHOLD
    has_buff = any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs)
    if above_threshold and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
        ))
    elif not above_threshold and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


# ---------------------------------------------------------------------------
# S2: Boulder Cleave
# ---------------------------------------------------------------------------

def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Chyue S2 Boulder Cleave — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# ---------------------------------------------------------------------------
# S3: Colossus Strike (ammo-based)
# ---------------------------------------------------------------------------

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    world.log(f"Chyue S3 Colossus Strike — ATK+{_S3_ATK_RATIO:.0%}, ammo={_S3_AMMO}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_chyue(slot: str = "S3") -> UnitState:
    """Chyue E2 max. Stone Aegis: SP-threshold ATK buff. S3: ammo burst."""
    op = _base_stats()
    op.name = "Chyue"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = SWORDMASTER_RANGE
    op.block = 1
    op.cost = 11

    op.talents = [TalentComponent(name="Stone Aegis", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Boulder Cleave",
            slot="S2",
            sp_cost=15,
            initial_sp=8,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Colossus Strike",
            slot="S3",
            sp_cost=30,
            initial_sp=15,
            duration=0.0,
            ammo_count=_S3_AMMO,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
