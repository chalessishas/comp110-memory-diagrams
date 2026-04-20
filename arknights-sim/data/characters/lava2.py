"""Lava the Purgatory (炎狱炎熔) — 6★ Caster (Splash Caster archetype).

CASTER_SPLASH trait: Each attack deals Arts AoE damage in a radius around the
  primary target (splash_radius = 0.8 tiles). All enemies within the radius
  receive full Arts damage simultaneously with the primary hit.

Talent "Thermal Conduction": When 2 or more enemies are in attack range, gain
  ATK+20%. Applied each tick while condition holds; removed when below threshold.

S2 "Scorched Earth": 25s duration. Splash radius expands to 1.5 tiles and
  ATK+30%. Wider AoE enables hitting tightly grouped enemy waves.
  sp_cost=35, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_1011_lava2).
  HP=1543, ATK=888, DEF=115, RES=20, atk_interval=2.9s, cost=35, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.lava2 import make_lava2 as _base_stats


# Standard long-range caster range: 4 tiles ahead × 3 rows
SPLASH_CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 5) for dy in range(-1, 2)
))

# Trait: splash AoE radius
_TRAIT_SPLASH_RADIUS = 0.8    # tiles — hits enemies within 0.8 tile radius of target

# Talent: Thermal Conduction
_TALENT_TAG = "lava2_thermal_conduction"
_TALENT_ATK_RATIO = 0.20      # +20% ATK when 2+ enemies in range
_TALENT_BUFF_TAG = "lava2_thermal_buff"
_TALENT_THRESHOLD = 2         # min enemies in range to activate

# S2: Scorched Earth
_S2_TAG = "lava2_s2_scorched_earth"
_S2_SPLASH_RADIUS = 1.5       # expanded splash radius during S2
_S2_ATK_RATIO = 0.30          # +30% ATK during S2
_S2_ATK_BUFF_TAG = "lava2_s2_atk"
_S2_DURATION = 25.0


def _enemies_in_range(op: UnitState, world) -> int:
    if op.position is None:
        return 0
    ox, oy = op.position
    count = 0
    for enemy in world.enemies():
        if not enemy.alive or not enemy.deployed or enemy.position is None:
            continue
        ex, ey = enemy.position
        dx = round(ex) - round(ox)
        dy = round(ey) - round(oy)
        if (dx, dy) in set(op.range_shape.tiles):
            count += 1
    return count


def _thermal_on_tick(world, carrier: UnitState, dt: float) -> None:
    in_range = _enemies_in_range(carrier, world)
    has_buff = any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs)
    if in_range >= _TALENT_THRESHOLD:
        if not has_buff:
            carrier.buffs.append(Buff(
                axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
            ))
    else:
        if has_buff:
            carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(_TALENT_TAG, on_tick=_thermal_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.splash_radius = _S2_SPLASH_RADIUS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.splash_radius = _TRAIT_SPLASH_RADIUS
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_lava2(slot: str = "S2") -> UnitState:
    """Lava the Purgatory E2 max. CASTER_SPLASH: 0.8-tile AoE always. S2: 1.5-tile AoE + ATK+30%."""
    op = _base_stats()
    op.name = "Lava the Purgatory"
    op.archetype = RoleArchetype.CASTER_SPLASH
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.attack_range_melee = False
    op.range_shape = SPLASH_CASTER_RANGE
    op.block = 1
    op.cost = 35
    op.splash_radius = _TRAIT_SPLASH_RADIUS
    op.splash_atk_multiplier = 1.0    # full damage to splash targets

    op.talents = [TalentComponent(name="Thermal Conduction", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Scorched Earth",
            slot="S2",
            sp_cost=35,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
