"""Broca (布洛卡) — 5★ Guard (Instructor archetype).

GUARD_INSTRUCTOR trait: Each attack also deals physical damage to all enemies
  adjacent (Manhattan ≤1) to the target. Implemented via splash_radius=1.0.

Talent "Regroup" (E2):
  While Broca is blocking at least 1 enemy, all nearby allied operators within
  2 tiles recover _REGEN_HEAL_RATIO×ATK HP per tick (passive HoT aura).

S2 "All In": MANUAL.
  ATK +_S2_ATK_RATIO, DEF +_S2_DEF_RATIO for _S2_DURATION seconds.
  sp_cost=40, initial_sp=20, AUTO_TIME + AUTO trigger.

S3 "Decisive Battle": MANUAL.
  ATK +160%, DEF +75% for 25s. splash_atk_multiplier boosted to 1.5.
  sp_cost=40, initial_sp=20, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100, char_356_broca):
  HP=2335, ATK=842, DEF=366, RES=0, atk_interval=1.2s, cost=23, block=3.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.broca import make_broca as _base_stats


INSTRUCTOR_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "broca_regroup"
_TALENT_REGEN_RATIO = 0.05    # 5% of Broca's ATK as HoT per tick to nearby allies
_TALENT_RANGE = 2              # Manhattan distance for the HoT aura

_S2_TAG = "broca_s2_all_in"
_S2_ATK_RATIO = 0.65
_S2_DEF_RATIO = 0.30
_S2_ATK_BUFF_TAG = "broca_s2_atk"
_S2_DEF_BUFF_TAG = "broca_s2_def"
_S2_DURATION = 20.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed or carrier.position is None:
        return
    # Only active when blocking
    blocking = sum(1 for e in world.enemies() if carrier.unit_id in e.blocked_by_unit_ids)
    if blocking == 0:
        return
    cx, cy = carrier.position
    heal_per_tick = int(carrier.effective_atk * _TALENT_REGEN_RATIO)
    if heal_per_tick <= 0:
        return
    for ally in world.allies():
        if ally is carrier or not ally.deployed or ally.position is None:
            continue
        if ally.hp >= ally.max_hp:
            continue
        dx = abs(round(ally.position[0]) - round(cx))
        dy = abs(round(ally.position[1]) - round(cy))
        if dx + dy <= _TALENT_RANGE:
            ally.heal(heal_per_tick)


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


# --- S3: Decisive Battle — ATK+160%, DEF+75%, splash boost, 25s MANUAL ---
_S3_TAG = "broca_s3_decisive_battle"
_S3_ATK_RATIO = 1.60
_S3_DEF_RATIO = 0.75
_S3_SPLASH_MULT = 1.5           # enhanced splash during S3
_S3_ATK_BUFF_TAG = "broca_s3_atk"
_S3_DEF_BUFF_TAG = "broca_s3_def"
_S3_DURATION = 25.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S3_DEF_RATIO, source_tag=_S3_DEF_BUFF_TAG,
    ))
    carrier._broca_s3_splash = carrier.splash_atk_multiplier
    carrier.splash_atk_multiplier = _S3_SPLASH_MULT
    world.log(f"Broca S3 Decisive Battle — ATK+{_S3_ATK_RATIO:.0%}, DEF+{_S3_DEF_RATIO:.0%}, splash×{_S3_SPLASH_MULT}")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG)]
    carrier.splash_atk_multiplier = getattr(carrier, "_broca_s3_splash", 1.0)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_broca(slot: str = "S2") -> UnitState:
    """Broca E2 max. Trait: splash to adjacent enemies. Talent: HoT aura while blocking."""
    op = _base_stats()
    op.name = "Broca"
    op.archetype = RoleArchetype.GUARD_INSTRUCTOR
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = INSTRUCTOR_RANGE
    op.block = 3
    op.cost = 23
    # GUARD_INSTRUCTOR trait: splash to adjacent enemies of target (radius ≤1 tile)
    op.splash_radius = 1.0
    op.splash_atk_multiplier = 1.0

    op.talents = [TalentComponent(name="Regroup", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="All In",
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
            name="Decisive Battle",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=True,
            behavior_tag=_S3_TAG,
        )
    return op
