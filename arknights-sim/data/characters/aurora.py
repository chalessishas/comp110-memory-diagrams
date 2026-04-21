"""Aurora (极光) — 5* Defender (Duelist archetype).

Duelist: block=1 base. Uses ice/cold attacks.

S1 "Defend the Homeland" (固守家园): 30s MANUAL.
  DEF +210%, block +2, STUN 5s all enemies in range on activation.
  sp_cost=20, initial_sp=10, MANUAL, AUTO_TIME.

S2 "Artificial Snowfall" (人工降雪): instant MANUAL (duration=0).
  ATK +75%, base_attack_time ×0.25 (very fast 1 burst attack with COLD).
  sp_cost=20, initial_sp=13, MANUAL, AUTO_TIME.
  (COLD status and actual attack burst not modeled — ATK buff and ASPD debuff only.)

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, StatusKind,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.aurora import make_aurora as _base_stats


MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1: Defend the Homeland ---
_S1_TAG = "aurora_s1_defend_homeland"
_S1_DEF_RATIO = 2.10
_S1_DEF_BUFF_TAG = "aurora_s1_def"
_S1_BLOCK_BONUS = 2
_S1_STUN_DURATION = 5.0
_S1_STUN_TAG = "aurora_s1_stun"
_S1_DURATION = 30.0

# --- S2: Artificial Snowfall (instant) ---
_S2_TAG = "aurora_s2_snowfall"
_S2_ATK_RATIO = 0.75
_S2_BUFF_TAG = "aurora_s2_atk"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG,
    ))
    carrier.block += _S1_BLOCK_BONUS
    if carrier.position is not None:
        cx, cy = carrier.position
        elapsed = world.global_state.elapsed
        tiles = set(carrier.range_shape.tiles)
        for e in world.enemies():
            if not e.alive or e.position is None:
                continue
            if (round(e.position[0]) - round(cx), round(e.position[1]) - round(cy)) not in tiles:
                continue
            e.statuses = [s for s in e.statuses if s.source_tag != _S1_STUN_TAG]
            e.statuses.append(StatusEffect(
                kind=StatusKind.STUN,
                source_tag=_S1_STUN_TAG,
                expires_at=elapsed + _S1_STUN_DURATION,
            ))
    world.log(f"Aurora S1 — DEF+{_S1_DEF_RATIO:.0%} block+{_S1_BLOCK_BONUS} STUN({_S1_STUN_DURATION}s)/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_DEF_BUFF_TAG]
    carrier.block -= _S1_BLOCK_BONUS


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    # Instant MANUAL: apply ATK buff permanently (duration=0, no on_end called)
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Aurora S2 Artificial Snowfall — ATK+{_S2_ATK_RATIO:.0%} (instant burst)")


register_skill(_S2_TAG, on_start=_s2_on_start)


def make_aurora(slot: str = "S1") -> UnitState:
    """Aurora E2 max. S1: DEF+210%+block+2+STUN/30s. S2: instant ATK+75%."""
    op = _base_stats()
    op.name = "Aurora"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Defend the Homeland",
            slot="S1",
            sp_cost=20,
            initial_sp=10,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Artificial Snowfall",
            slot="S2",
            sp_cost=20,
            initial_sp=13,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
