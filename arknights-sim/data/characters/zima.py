"""Zima (吉娜) — 5* Vanguard (Pioneer archetype).

Talent "Lead Whistle": When deployed, all ground enemies within 3 Manhattan
  tiles are stunned for 3s. Fires via on_battle_start (world.add_unit).

S2 "Battle Cry": 25s duration, ATK +80%.
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger, requires_target=True.

S3 "March Order": Instantly grants 15 DP, then for 25s applies ATK+60% aura
  (TTL-stamp) to all deployed Vanguard allies. MANUAL.
  sp_cost=45, initial_sp=15, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.zima import make_zima as _base_stats


VANGUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Lead Whistle ---
_TALENT_TAG = "zima_lead_whistle"
_STUN_DURATION = 3.0
_STUN_TAG = "zima_stun"
_STUN_RANGE = 3   # Manhattan distance threshold

# --- S2: Battle Cry ---
_S2_TAG = "zima_s2_battle_cry"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "zima_s2_atk_buff"
_S2_DURATION = 25.0


def _talent_on_battle_start(world, unit: UnitState) -> None:
    if unit.position is None:
        return
    ux, uy = unit.position
    for enemy in world.enemies():
        if not enemy.alive or enemy.position is None:
            continue
        dx = abs(enemy.position[0] - ux)
        dy = abs(enemy.position[1] - uy)
        if dx + dy <= _STUN_RANGE:
            enemy.statuses.append(StatusEffect(
                kind=StatusKind.STUN,
                source_tag=_STUN_TAG,
                expires_at=world.global_state.elapsed + _STUN_DURATION,
            ))
            world.log(
                f"Zima Lead Whistle → {enemy.name}  stun ({_STUN_DURATION}s)"
            )


register_talent(_TALENT_TAG, on_battle_start=_talent_on_battle_start)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: March Order — 15 DP instant + ATK+60% to all deployed Vanguards for 25s ---
_S3_TAG = "zima_s3_march_order"
_S3_DP_GAIN = 15
_S3_ATK_RATIO = 0.60
_S3_DURATION = 25.0
_S3_ATK_BUFF_TAG = "zima_s3_atk"


def _s3_on_start(world, carrier: UnitState) -> None:
    world.global_state.refund_dp(_S3_DP_GAIN)
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        if ally.profession != Profession.VANGUARD:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
        ))
    world.log(f"Zima S3 March Order — {_S3_DP_GAIN} DP + ATK+{_S3_ATK_RATIO:.0%} to Vanguards")


def _s3_on_end(world, carrier: UnitState) -> None:
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_zima(slot: str = "S2") -> UnitState:
    """Zima E2 max. Talent: STUN on deploy. S2: ATK burst."""
    op = _base_stats()
    op.name = "Zima"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VANGUARD_RANGE
    op.cost = 14

    op.talents = [TalentComponent(name="Lead Whistle", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Battle Cry",
            slot="S2",
            sp_cost=40,
            initial_sp=20,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="March Order",
            slot="S3",
            sp_cost=45,
            initial_sp=15,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
