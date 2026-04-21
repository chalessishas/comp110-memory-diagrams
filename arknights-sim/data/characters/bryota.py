"""苍苔 (Bryota) — 5★ Guard (Fighter archetype).

S1 "强力击·β型": sp_cost=3, initial_sp=0, duration=0 (instant AUTO_ATTACK).
  ATK×230% — instant hit, not modeled.

S2 "土石的恒心": sp_cost=50, initial_sp=35, duration=30s, MANUAL, AUTO_TIME.
  ATK +80%, DEF +80%, STUN 5s all enemies in range on activation.
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
from data.characters.generated.bryota import make_bryota as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

# --- S1 stub ---
_S1_TAG = "bryota_s1_power_strike"
_S1_ATK_SCALE = 2.30

# --- S2 ---
_S2_TAG = "bryota_s2_steadfast_rock"
_S2_ATK_RATIO = 0.80
_S2_DEF_RATIO = 0.80
_S2_STUN_DURATION = 5.0
_S2_ATK_BUFF_TAG = "bryota_s2_atk"
_S2_DEF_BUFF_TAG = "bryota_s2_def"
_S2_STUN_TAG = "bryota_s2_stun"
_S2_DURATION = 30.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    if carrier.position is not None:
        cx, cy = carrier.position
        elapsed = world.global_state.elapsed
        tiles = set(carrier.range_shape.tiles)
        for e in world.enemies():
            if not e.alive or e.position is None:
                continue
            if (round(e.position[0]) - round(cx), round(e.position[1]) - round(cy)) not in tiles:
                continue
            e.statuses = [s for s in e.statuses if s.source_tag != _S2_STUN_TAG]
            e.statuses.append(StatusEffect(
                kind=StatusKind.STUN,
                source_tag=_S2_STUN_TAG,
                expires_at=elapsed + _S2_STUN_DURATION,
            ))
    world.log(f"Bryota S2 — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%} STUN({_S2_STUN_DURATION}s)/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_bryota(slot: str = "S2") -> UnitState:
    """Bryota E2 max. S1: instant ATK×230% (not modeled). S2: ATK+80%+DEF+80%+STUN/30s."""
    op = _base_stats()
    op.name = "Bryota"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="Power Strike β",
            slot="S1",
            sp_cost=3,
            initial_sp=0,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Steadfast as Rock",
            slot="S2",
            sp_cost=50,
            initial_sp=35,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
