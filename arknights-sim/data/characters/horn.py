"""Horn — 6* Defender (Fortress archetype).

Fortress class trait: attacks all enemies in range when NOT blocking (ranged physical AoE);
when blocking, attacks single target (melee mode). ATK interval switches too:
  - Ranged mode: 2.8s (E2 base)
  - Melee mode:  2.8s (same for Horn, unlike some Fortress variants)

Range shapes (from ArknightsGameData — Defender Grid, Horn E2):
  - Ranged (not blocking): cross extending 3 tiles forward + 1 tile side
  - Melee (blocking): operator tile + 1 forward

Talent "Pioneer's Creed" (E2): ATK +12% (implemented as a passive RATIO buff).

S2 "Support Ray": ATK +120%, forces ranged attack mode even while blocking.
  Duration=35s, sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=False.
  While active: _force_ranged_mode=True overrides the blocking check in targeting_system.

Base stats from ArknightsGameData (E2 max, trust 100).
  HP=4400, ATK=592, DEF=580, RES=0, atk_interval=2.8s, cost=28, block=3.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.horn import make_horn as _base_stats


# Ranged mode: 3-tile forward line + 1-tile forward sides
_RANGED_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1),
))

# Melee mode: standard close combat
_MELEE_RANGE = RangeShape(tiles=(
    (0, 0), (1, 0),
))

# --- Talent: Pioneer's Creed ---
_TALENT_TAG = "horn_pioneers_creed"
_TALENT_ATK_RATIO = 0.12     # +12% ATK passive
_TALENT_BUFF_TAG = "horn_talent_atk"


def _talent_on_battle_start(world, carrier: UnitState) -> None:
    if not carrier.deployed:
        return
    # Avoid double-applying if already buffed
    if any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs):
        return
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
    ))


def _talent_on_deploy(world, carrier: UnitState) -> None:
    if any(b.source_tag == _TALENT_BUFF_TAG for b in carrier.buffs):
        return
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_TALENT_ATK_RATIO, source_tag=_TALENT_BUFF_TAG,
    ))


def _talent_on_retreat(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]


register_talent(
    _TALENT_TAG,
    on_battle_start=_talent_on_battle_start,
    on_deploy=_talent_on_deploy,
    on_retreat=_talent_on_retreat,
)


# --- S2: Support Ray ---
_S2_TAG = "horn_s2_support_ray"
_S2_ATK_RATIO = 1.20         # ATK +120%
_S2_BUFF_TAG = "horn_s2_atk"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    carrier._force_ranged_mode = True
    world.log(f"Horn S2 Support Ray — ATK +{_S2_ATK_RATIO:.0%}, forced ranged mode")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]
    carrier._force_ranged_mode = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_horn(slot: str = "S2", talent: bool = True) -> UnitState:
    """Horn E2 max. Fortress: ranged AoE / melee toggle. S2: ATK+120% + forced ranged mode."""
    op = _base_stats()
    op.name = "Horn"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.block = 3
    op.cost = 28

    op.range_shape = _RANGED_RANGE
    op._melee_range = _MELEE_RANGE

    if talent:
        op.talents = [TalentComponent(name="Pioneer's Creed", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Support Ray",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=35.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
