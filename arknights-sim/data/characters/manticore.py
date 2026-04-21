"""Manticore (狮蝎) — 5* Specialist (Executor archetype).

Talent "Venomous Fangs": While deployed, Manticore passively maintains CAMOUFLAGE.

S1 "Scorpion's Art": self-REGEN 150 HP/s, 8s. sp_cost=10, initial_sp=5, AUTO.

S2 "Predator's Claws": ATK+100%, BIND (2s) all enemies in range at activation.
  sp_cost=20, initial_sp=5, 15s, AUTO.

S3 "Predator's Domain" (猎域): MANUAL, 20s duration.
  ATK+200%, BIND (4s) all enemies in range at activation.
  sp_cost=45, initial_sp=15, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, RangeShape, TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind, TICK_RATE,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.mantic import make_mantic as _base_stats


EXECUTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Venomous Fangs (passive CAMOUFLAGE) ---
_TALENT_TAG = "manticore_camouflage"
_CAMO_TAG = "manticore_camo_aura"
_CAMO_REFRESH_DT = 2.0 / TICK_RATE   # two ticks — lapses quickly when undeployed

# --- S2: Predator's Claws ---
_S2_TAG = "manticore_s2_predator"
_S2_ATK_RATIO = 1.00         # ATK +100%
_S2_BIND_DURATION = 2.0      # 2s BIND on each hit enemy at skill start
_S2_BIND_TAG = "manticore_s2_bind"
_S2_BUFF_TAG = "manticore_s2_atk"

# --- S3: Predator's Domain ---
_S3_TAG = "manticore_s3_predator_domain"
_S3_ATK_RATIO = 2.00         # ATK +200%
_S3_BIND_DURATION = 4.0      # 4s BIND on all enemies in range
_S3_BIND_TAG = "manticore_s3_bind"
_S3_BUFF_TAG = "manticore_s3_atk"
_S3_DURATION = 20.0


def _s2_on_start(world, carrier: UnitState) -> None:
    from core.state.unit_state import Buff
    from core.types import BuffAxis, BuffStack
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    if carrier.position is None:
        return
    cx, cy = carrier.position
    elapsed = world.global_state.elapsed
    tiles = set(carrier.range_shape.tiles)
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        if (round(e.position[0]) - round(cx), round(e.position[1]) - round(cy)) not in tiles:
            continue
        e.statuses = [s for s in e.statuses if s.source_tag != _S2_BIND_TAG]
        e.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S2_BIND_TAG,
            expires_at=elapsed + _S2_BIND_DURATION,
        ))
    world.log(f"Manticore S2 Predator's Claws — ATK+{_S2_ATK_RATIO:.0%}, BIND({_S2_BIND_DURATION}s)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    from core.state.unit_state import Buff
    from core.types import BuffAxis, BuffStack
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))
    if carrier.position is None:
        return
    cx, cy = carrier.position
    elapsed = world.global_state.elapsed
    tiles = set(carrier.range_shape.tiles)
    for e in world.enemies():
        if not e.alive or e.position is None:
            continue
        if (round(e.position[0]) - round(cx), round(e.position[1]) - round(cy)) not in tiles:
            continue
        e.statuses = [s for s in e.statuses if s.source_tag != _S3_BIND_TAG]
        e.statuses.append(StatusEffect(
            kind=StatusKind.BIND,
            source_tag=_S3_BIND_TAG,
            expires_at=elapsed + _S3_BIND_DURATION,
        ))
    world.log(f"Manticore S3 Predator's Domain — ATK+{_S3_ATK_RATIO:.0%}, BIND({_S3_BIND_DURATION}s)")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


# --- S1: Scorpion's Art (self-REGEN) ---
_S1_TAG = "manticore_s1_scorpion"
_S1_REGEN_HPS = 150.0        # 150 HP per second (true regen, bypasses DEF)
_S1_REGEN_DURATION = 8.0
_S1_REGEN_TAG = "manticore_s1_regen"


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    elapsed = world.global_state.elapsed
    expires = elapsed + _CAMO_REFRESH_DT
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _CAMO_TAG]
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.CAMOUFLAGE,
        source_tag=_CAMO_TAG,
        expires_at=expires,
    ))


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s1_on_start(world, carrier: UnitState) -> None:
    elapsed = world.global_state.elapsed
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _S1_REGEN_TAG]
    carrier.statuses.append(StatusEffect(
        kind=StatusKind.REGEN,
        source_tag=_S1_REGEN_TAG,
        expires_at=elapsed + _S1_REGEN_DURATION,
        params={"hps": _S1_REGEN_HPS},
    ))
    world.log(f"Manticore S1 → self REGEN {_S1_REGEN_HPS:.0f} HPS ({_S1_REGEN_DURATION}s)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.statuses = [s for s in carrier.statuses if s.source_tag != _S1_REGEN_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_manticore(slot: str = "S1") -> UnitState:
    """Manticore E2 max. Talent: passive CAMOUFLAGE while deployed. S1: self-REGEN 150 HPS/8s."""
    op = _base_stats()
    op.name = "Manticore"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = EXECUTOR_RANGE
    op.cost = 20
    op.block = 0

    op.talents = [TalentComponent(name="Venomous Fangs", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Predator's Claws",
            slot="S2",
            sp_cost=20,
            initial_sp=5,
            duration=15.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S1":
        op.skill = SkillComponent(
            name="Scorpion's Art",
            slot="S1",
            sp_cost=10,
            initial_sp=5,
            duration=_S1_REGEN_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Predator's Domain",
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
