"""Ashlock (灰毫) — 5* Defender (Fortress archetype).

Fortress class trait: attacks all enemies in range when NOT blocking (ranged physical AoE);
when blocking, attacks single target (melee mode). Identical archetype behavior to Horn.

Range shapes follow the same pattern as Horn (ArknightsGameData Fortress Defender grid):
  - Ranged: 3-tile forward line + side tiles
  - Melee:  operator tile + 1 tile forward

S2 "Torrent": ATK +80%, forces ranged mode even while blocking, for 25s.
  sp_cost=25, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=False.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.ashlok import make_ashlok as _base_stats


# --- Talent: Steadfast Guard — permanent flat DEF bonus ---
_TALENT_TAG = "ashlock_steadfast_guard"
_TALENT_BUFF_TAG = "ashlock_steadfast_guard_def"
_DEF_BONUS = 150


def _steadfast_on_battle_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_DEF_BONUS, source_tag=_TALENT_BUFF_TAG,
    ))
    world.log(f"Ashlock Steadfast Guard — DEF +{_DEF_BONUS}")


register_talent(_TALENT_TAG, on_battle_start=_steadfast_on_battle_start)


_RANGED_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1),
))

_MELEE_RANGE = RangeShape(tiles=(
    (0, 0), (1, 0),
))

# --- S2: Torrent ---
_S2_TAG = "ashlock_s2_torrent"
_S2_ATK_RATIO = 0.80     # ATK +80%
_S2_SOURCE_TAG = "ashlock_s2_torrent"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    carrier._force_ranged_mode = True
    world.log(f"Ashlock S2 Torrent — ATK +{_S2_ATK_RATIO:.0%}, forced ranged mode")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]
    carrier._force_ranged_mode = False


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_ashlock(slot: str = "S2") -> UnitState:
    """Ashlock E2 max. Fortress: ranged AoE ↔ melee toggle. S2: ATK+80% + forced ranged 25s."""
    op = _base_stats()
    op.name = "Ashlock"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.block = 3
    op.cost = 27
    op.talents = [TalentComponent(name="Steadfast Guard", behavior_tag=_TALENT_TAG)]

    op.range_shape = _RANGED_RANGE
    op._melee_range = _MELEE_RANGE

    if slot == "S2":
        op.skill = SkillComponent(
            name="Torrent",
            slot="S2",
            sp_cost=25,
            initial_sp=10,
            duration=25.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
