"""Meteorite (陨星) — 5★ Sniper (Artillery archetype).

SNIPER_ARTILLERY trait: Each attack deals physical splash damage to all enemies
  within _BASE_SPLASH_RADIUS tiles of the target. Uses existing splash_radius system.

Talent "Landing Blast" (E2):
  On attack hit, apply DEF_DOWN (_TALENT_DEF_DOWN_RATIO) to the primary target for
  _TALENT_DEF_DOWN_DURATION seconds. Status+Buff pair (DEF axis, negative ratio).

S2 "Shock Zone": MANUAL.
  ATK +_S2_ATK_RATIO, splash_radius increases to _S2_SPLASH_RADIUS for _S2_DURATION.
  sp_cost=45, initial_sp=20, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_219_meteo):
  HP=1505, ATK=950, DEF=116, RES=0, atk_interval=2.8s, cost=28, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
    TalentComponent, StatusEffect,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode, StatusKind,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.meteo import make_meteo as _base_stats


ARTILLERY_RANGE = RangeShape(tiles=tuple(
    (dx, dy)
    for dx in range(1, 6)
    for dy in range(-1, 2)
))

_BASE_SPLASH_RADIUS = 1.1

_TALENT_TAG = "meteo_landing_blast"
_TALENT_DEF_DOWN_RATIO = 0.10    # -10% DEF
_TALENT_DEF_DOWN_DURATION = 6.0
_TALENT_DEF_DOWN_TAG = "meteo_def_down"

_S2_TAG = "meteo_s2_shock_zone"
_S2_ATK_RATIO = 0.50
_S2_ATK_BUFF_TAG = "meteo_s2_atk"
_S2_SPLASH_RADIUS = 1.8
_S2_DURATION = 15.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    elapsed = world.global_state.elapsed
    target.statuses = [s for s in target.statuses if s.source_tag != _TALENT_DEF_DOWN_TAG]
    target.buffs = [b for b in target.buffs if b.source_tag != _TALENT_DEF_DOWN_TAG]
    target.statuses.append(StatusEffect(
        kind=StatusKind.DEF_DOWN,
        source_tag=_TALENT_DEF_DOWN_TAG,
        expires_at=elapsed + _TALENT_DEF_DOWN_DURATION,
        params={"ratio": _TALENT_DEF_DOWN_RATIO},
    ))
    target.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=-_TALENT_DEF_DOWN_RATIO,
        source_tag=_TALENT_DEF_DOWN_TAG,
        expires_at=elapsed + _TALENT_DEF_DOWN_DURATION,
    ))
    world.log(
        f"Meteorite Landing Blast → {target.name}  "
        f"DEF_DOWN -{_TALENT_DEF_DOWN_RATIO:.0%} ({_TALENT_DEF_DOWN_DURATION}s)"
    )


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.splash_radius = _S2_SPLASH_RADIUS


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]
    carrier.splash_radius = _BASE_SPLASH_RADIUS


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_meteo(slot: str = "S2") -> UnitState:
    """Meteorite E2 max. Trait: physical splash. Talent: DEF_DOWN on hit. S2: ATK+50% + wider splash."""
    op = _base_stats()
    op.name = "Meteorite"
    op.archetype = RoleArchetype.SNIPER_ARTILLERY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = False
    op.range_shape = ARTILLERY_RANGE
    op.block = 1
    op.cost = 28
    op.splash_radius = _BASE_SPLASH_RADIUS
    op.splash_atk_multiplier = 1.0

    op.talents = [TalentComponent(name="Landing Blast", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Shock Zone",
            slot="S2",
            sp_cost=45,
            initial_sp=20,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
