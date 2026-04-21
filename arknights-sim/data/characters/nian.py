"""Nian (年) — 6★ Defender (Protector archetype).

Talent "Clairvoyance": After deployment, immediately gains 3 Shields.
  Each shield pool = max_hp (approx: one shield per hit, capped at max_hp).

S2 "Copper Seal" (M3): 35s, MANUAL, sp_cost=50, initial_sp=35, AUTO_TIME.
  Stops attacking (atk_cd frozen). DEF+130%, Block+1.
  When Nian receives a hit: deal Arts damage = 90% ATK to attacker + Silence 5s.

S3 "Iron Defense" (M3): 45s, MANUAL, sp_cost=85, initial_sp=70, AUTO_TIME.
  ATK+120%. All nearby allied operators gain DEF+80%, Block+1.

Base stats (E2 max, trust 100, char_2014_nian):
  HP=4099, ATK=619, DEF=796, RES=0, atk_interval=1.5, block=3, cost=23.
"""
from __future__ import annotations

from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.nian import make_nian as _base_stats


PROTECTOR_RANGE = RangeShape(tiles=((1, 0), (2, 0), (1, -1), (1, 1)))
_S3_RANGE = 2  # Chebyshev distance for Iron Defense ally buff

_TALENT_TAG = "nian_clairvoyance"
_SHIELD_PER_CHARGE = 4099  # approx one max_hp per shield charge
_SHIELD_TAG = "nian_clairvoyance_shield"
_SHIELD_CHARGES = 3

_S2_TAG = "nian_s2_copper_seal"
_S2_DEF_RATIO = 1.30          # DEF+130%
_S2_DEF_BUFF_TAG = "nian_s2_def"
_S2_COUNTER_RATIO = 0.90      # 90% ATK Arts counter
_S2_SILENCE_DURATION = 5.0

_S3_TAG = "nian_s3_iron_defense"
_S3_ATK_RATIO = 1.20          # ATK+120%
_S3_ATK_BUFF_TAG = "nian_s3_atk"
_S3_ALLY_DEF_RATIO = 0.80     # DEF+80% to nearby allies
_S3_ALLY_DEF_BUFF_TAG = "nian_s3_ally_def"
_S3_DURATION = 45.0


# ── Talent ──────────────────────────────────────────────────────────────────

def _on_deploy(world, carrier: UnitState) -> None:
    """Grant 3 Shield charges on deployment."""
    for _ in range(_SHIELD_CHARGES):
        carrier.statuses.append(StatusEffect(
            kind=StatusKind.SHIELD,
            source_tag=_SHIELD_TAG,
            expires_at=float("inf"),
            params={"amount": float(_SHIELD_PER_CHARGE)},
        ))
    world.log(f"Nian Clairvoyance — {_SHIELD_CHARGES} shields granted")


def _on_hit_received(world, carrier: UnitState, attacker, damage: int) -> None:
    """S2 counter: when hit during Copper Seal, deal Arts and silence attacker."""
    if not getattr(carrier, "_nian_s2_active", False):
        return
    if attacker is None:
        return
    arts_dmg = attacker.take_arts(int(carrier.effective_atk * _S2_COUNTER_RATIO))
    world.global_state.total_damage_dealt += arts_dmg
    attacker.statuses.append(StatusEffect(
        kind=StatusKind.SILENCE,
        source_tag="nian_s2_silence",
        expires_at=world.global_state.elapsed + _S2_SILENCE_DURATION,
        params={},
    ))
    world.log(f"Nian Copper Seal counter → {attacker.name}  arts={arts_dmg} silence={_S2_SILENCE_DURATION}s")


register_talent(_TALENT_TAG, on_deploy=_on_deploy, on_hit_received=_on_hit_received)


# ── S2: Copper Seal ──────────────────────────────────────────────────────────

def _s2_on_start(world, carrier: UnitState) -> None:
    carrier._nian_s2_active = True
    carrier._nian_s2_saved_block = carrier.block
    carrier.block = carrier.block + 1
    carrier._nian_s2_saved_atk_cd = carrier.atk_cd
    carrier.atk_cd = 9999.0       # disarmed for skill duration
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    world.log(f"Nian Copper Seal — DEF+{_S2_DEF_RATIO:.0%}, Block+1, disarmed")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier._nian_s2_active = False
    carrier.block = getattr(carrier, "_nian_s2_saved_block", 3)
    carrier.atk_cd = carrier.current_atk_interval
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_DEF_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# ── S3: Iron Defense ─────────────────────────────────────────────────────────

def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier._nian_s3_buffed_allies: list[int] = []
    if carrier.position is None:
        return
    cx, cy = carrier.position
    for ally in world.allies():
        if ally is carrier or not ally.alive or not ally.deployed or ally.position is None:
            continue
        ax, ay = ally.position
        if max(abs(ax - cx), abs(ay - cy)) <= _S3_RANGE:
            ally.buffs.append(Buff(
                axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                value=_S3_ALLY_DEF_RATIO, source_tag=_S3_ALLY_DEF_BUFF_TAG,
            ))
            ally.block += 1
            carrier._nian_s3_buffed_allies.append(ally.unit_id)
    world.log(f"Nian Iron Defense — ATK+{_S3_ATK_RATIO:.0%}, allies DEF+{_S3_ALLY_DEF_RATIO:.0%}, Block+1")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    buffed_ids = set(getattr(carrier, "_nian_s3_buffed_allies", []))
    for ally in world.allies():
        if ally.unit_id in buffed_ids:
            ally.buffs = [b for b in ally.buffs if b.source_tag != _S3_ALLY_DEF_BUFF_TAG]
            ally.block = max(1, ally.block - 1)
    carrier._nian_s3_buffed_allies = []


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ── Factory ──────────────────────────────────────────────────────────────────

def make_nian(slot: str = "S2") -> UnitState:
    """Nian E2 max. Talent: 3 Shields on deploy. S2: Copper Seal (disarm+DEF+counter). S3: Iron Defense (ATK+ally DEF+Block)."""
    op = _base_stats()
    op.name = "Nian"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = PROTECTOR_RANGE
    op.block = 3
    op.cost = 23
    op.max_hp = 4099
    op.hp = 4099
    op.atk = 619
    op.defence = 796

    op.talents = [TalentComponent(name="Clairvoyance", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Copper Seal",
            slot="S2",
            sp_cost=50,
            initial_sp=35,
            duration=35.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Iron Defense",
            slot="S3",
            sp_cost=85,
            initial_sp=70,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
