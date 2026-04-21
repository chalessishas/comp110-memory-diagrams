"""Amiya (阿米娅) — 6★ Core Caster, main character of Arknights.

Talent "Sarkaz King": When Amiya kills an enemy, recover 8 SP.

S1 "Tactical Chant γ" (M3): ASPD +80 for 30 s.
  MANUAL, sp_cost=35, initial_sp=5.

S2 "Spirit Burst" (M3): Each attack fires 6 projectiles at ~65% ATK each.
  Modelled as ATK_RATIO +2.90 (≈ 6×65% total per attack cycle). 25 s, AUTO, sp_cost=100.
  After skill ends: Amiya is self-Stunned for 10 s.

S3 "Chimera" (M3): ATK +240%, Max HP +100%, range expands to 6-col,
  damage type → TRUE. 30 s, MANUAL, sp_cost=120, initial_sp=0.
  After skill ends, Amiya is automatically retreated from the field.

Base stats (E2 max, trust 100, char_002_amiya):
  HP=1680, ATK=682, DEF=121, RES=20, atk_interval=1.6, block=1, cost=20.
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
from data.characters.generated.amiya import make_amiya as _base_stats


# Standard Core Caster range: 4 cols forward, 3 rows
CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))
# S3 Chimera expanded range: 6 cols forward
CHIMERA_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 5) for dy in range(-1, 2)
))

# ── Talent: Sarkaz King ───────────────────────────────────────────────────────
_TALENT_TAG = "amiya_sarkaz_king"
_TALENT_SP_ON_KILL = 8


def _on_kill(world, attacker: UnitState, target) -> None:
    sk = getattr(attacker, "skill", None)
    if sk is None or sk.active_remaining > 0:
        return
    sk.sp = min(float(sk.sp_cost), sk.sp + float(_TALENT_SP_ON_KILL))
    world.log(f"Amiya talent: kill → +{_TALENT_SP_ON_KILL} SP ({sk.sp:.0f}/{sk.sp_cost})")


register_talent(_TALENT_TAG, on_kill=_on_kill)


# ── S1: Tactical Chant γ ─────────────────────────────────────────────────────
_S1_TAG = "amiya_s1_tactical_chant"
_S1_ASPD_BONUS = 80.0
_S1_ASPD_BUFF_TAG = "amiya_s1_aspd"
_S1_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG,
    ))
    world.log(f"Amiya Tactical Chant γ — ASPD+{_S1_ASPD_BONUS:.0f}")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


# ── S2: Spirit Burst ──────────────────────────────────────────────────────────
_S2_TAG = "amiya_s2_spirit_burst"
_S2_ATK_RATIO = 2.90       # 6 shots × ~65% each → 390% total; ratio = +2.90
_S2_ATK_BUFF_TAG = "amiya_s2_atk"
_S2_STUN_TAG = "amiya_s2_self_stun"
_S2_STUN_DURATION = 10.0
_S2_DURATION = 25.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    world.log(f"Amiya Spirit Burst — ATK×{1 + _S2_ATK_RATIO:.1f} (6-shot burst)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.STUN,
        source_tag=_S2_STUN_TAG,
        expires_at=world.global_state.elapsed + _S2_STUN_DURATION,
        params={},
    ))
    world.log(f"Amiya Spirit Burst ends — self-Stun {_S2_STUN_DURATION}s")


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# ── S3: Chimera ───────────────────────────────────────────────────────────────
_S3_TAG = "amiya_s3_chimera"
_S3_ATK_RATIO = 2.40       # ATK +240%
_S3_HP_MULTIPLIER = 2      # Max HP ×2 (+100%)
_S3_ATK_BUFF_TAG = "amiya_s3_atk"
_S3_DURATION = 30.0


def _s3_on_start(world, carrier: UnitState) -> None:
    # ATK buff
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    # HP ×2: scale current hp proportionally
    old_max = carrier.max_hp
    carrier._amiya_s3_old_max_hp = old_max
    new_max = old_max * _S3_HP_MULTIPLIER
    carrier.max_hp = new_max
    carrier.hp = min(carrier.hp + (new_max - old_max), new_max)
    # Save original attack type and range
    carrier._amiya_s3_orig_attack_type = carrier.attack_type
    carrier._amiya_s3_orig_range = carrier.range_shape
    carrier.attack_type = AttackType.TRUE
    carrier.range_shape = CHIMERA_RANGE
    world.log(f"Amiya Chimera — ATK+{_S3_ATK_RATIO:.0%}, HP×{_S3_HP_MULTIPLIER}, TRUE dmg, range+")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]
    old_max = getattr(carrier, "_amiya_s3_old_max_hp", carrier.max_hp // _S3_HP_MULTIPLIER)
    carrier.max_hp = old_max
    carrier.hp = min(carrier.hp, old_max)
    carrier.attack_type = getattr(carrier, "_amiya_s3_orig_attack_type", AttackType.ARTS)
    carrier.range_shape = getattr(carrier, "_amiya_s3_orig_range", CASTER_RANGE)
    world.log("Amiya Chimera ends — auto-retreat")
    world.retreat(carrier)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# ── Factory ───────────────────────────────────────────────────────────────────

def make_amiya(slot: str = "S2") -> UnitState:
    """Amiya E2 max. S1: ASPD. S2: multi-hit burst + self-stun. S3: Chimera (TRUE + auto-retreat)."""
    op = _base_stats()
    op.name = "Amiya"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = CASTER_RANGE
    op.block = 1
    op.cost = 20
    op.max_hp = 1680
    op.hp = 1680
    op.atk = 682
    op.defence = 121
    op.res = 20.0

    op.talents = [TalentComponent(name="Sarkaz King", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Chant γ",
            slot="S1",
            sp_cost=35,
            initial_sp=5,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Spirit Burst",
            slot="S2",
            sp_cost=100,
            initial_sp=0,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Chimera",
            slot="S3",
            sp_cost=120,
            initial_sp=0,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
