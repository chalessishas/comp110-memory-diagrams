"""Ceylon (锡兰) — 6* Medic (Multi-Target archetype).

MEDIC_MULTI trait: heals 3 most-injured allies simultaneously per attack.

Talent "Calm Waters" (E2):
  All allies within _TALENT_RANGE tiles gain a passive DEF +30 flat buff.
  Implemented via on_tick — aura is added/removed dynamically as allies move.
  (Flat DEF is distinct from Toknogi's ratio DEF; both stack additively in
  effective_stat formula: FLOOR(base × ratio) × mult + flat.)

S3 "Quiet Recovery" (M3):
  Duration 30s.  Ceylon ATK +20%.  All allies within S3 range gain
  ATK_INTERVAL -0.30s (attack speed up) for the skill duration.
  Also raises heal targets from 3 → 5 while active.
  sp_cost=30, initial_sp=15, AUTO_TIME, MANUAL trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_348_ceylon).
  HP=1655, ATK=508, DEF=126, RES=10, atk_interval=2.85s, cost=22, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ceylon import make_ceylon as _base_stats


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

# --- Talent: Calm Waters (passive flat DEF aura) ---
_TALENT_TAG = "ceylon_calm_waters"
_TALENT_DEF_TAG = "ceylon_talent_def"
_TALENT_DEF_FLAT = 30          # +30 flat DEF to nearby allies
_TALENT_RANGE = 3              # Manhattan distance threshold

# --- S3: Quiet Recovery ---
_S3_TAG = "ceylon_s3_quiet_recovery"
_S3_ATK_RATIO = 0.20           # +20% ATK to Ceylon
_S3_ATK_BUFF_TAG = "ceylon_s3_atk"
_S3_INTERVAL_OFFSET = -0.30    # subtract 0.30s from atk_interval (faster attacks)
_S3_INTERVAL_BUFF_TAG = "ceylon_s3_interval"
_S3_HEAL_TARGETS = 5           # 3 → 5 during skill
_S3_DURATION = 30.0
_S3_RANGE = 3                  # Manhattan distance for S3 ASPD buff

_BASE_HEAL_TARGETS = 3


# ---------------------------------------------------------------------------
# Talent: Calm Waters — passive flat DEF aura
# ---------------------------------------------------------------------------

def _calm_waters_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    cx, cy = carrier.position
    for ally in world.allies():
        if ally is carrier or ally.position is None:
            continue
        ax, ay = ally.position
        in_range = (abs(ax - cx) + abs(ay - cy) <= _TALENT_RANGE)
        has_buff = any(b.source_tag == _TALENT_DEF_TAG for b in ally.buffs)
        if in_range and not has_buff:
            ally.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.FLAT,
                value=_TALENT_DEF_FLAT, source_tag=_TALENT_DEF_TAG,
            ))
        elif not in_range and has_buff:
            ally.buffs = [b for b in ally.buffs if b.source_tag != _TALENT_DEF_TAG]


register_talent(_TALENT_TAG, on_tick=_calm_waters_on_tick)


# ---------------------------------------------------------------------------
# S3: Quiet Recovery
# ---------------------------------------------------------------------------

def _allies_in_s3_range(world, carrier: UnitState):
    if carrier.position is None:
        return []
    cx, cy = carrier.position
    return [
        ally for ally in world.allies()
        if ally is not carrier
        and ally.alive and ally.deployed
        and ally.position is not None
        and abs(ally.position[0] - cx) + abs(ally.position[1] - cy) <= _S3_RANGE
    ]


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.heal_targets = _S3_HEAL_TARGETS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    for ally in _allies_in_s3_range(world, carrier):
        if not any(b.source_tag == _S3_INTERVAL_BUFF_TAG for b in ally.buffs):
            ally.buffs.append(Buff(
                axis=BuffAxis.ATK_INTERVAL, stack=BuffStack.FLAT,
                value=_S3_INTERVAL_OFFSET, source_tag=_S3_INTERVAL_BUFF_TAG,
            ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.heal_targets = _BASE_HEAL_TARGETS
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_INTERVAL_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_ceylon(slot: str = "S3") -> UnitState:
    """Ceylon E2 max. MEDIC_MULTI: heals 3 allies. Talent: flat DEF+30 aura. S3: ASPD buff."""
    op = _base_stats()
    op.name = "Ceylon"
    op.archetype = RoleArchetype.MEDIC_MULTI
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.attack_range_melee = False
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 22
    op.heal_targets = _BASE_HEAL_TARGETS

    op.talents = [TalentComponent(
        name="Calm Waters",
        behavior_tag=_TALENT_TAG,
    )]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Quiet Recovery",
            slot="S3",
            sp_cost=30,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
