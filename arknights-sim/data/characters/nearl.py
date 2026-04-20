"""Nearl (临光) — 6* Defender (Knight archetype).

Talent "Holy Knight's Light" (E2): Every 25s, restores HP equal to 8% of max_hp
  to all allies within range (5-tile cross). Passive, fires via on_tick accumulator.

S2 "Justice": ATK +100%, DEF +55%, duration 30s.
  sp_cost=30, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.
  Dual-axis buff: both ATK and DEF buffs apply/clear together.

Base stats from ArknightsGameData (E2 max, trust 100, char_148_nearl).
  HP=2780, ATK=502, DEF=625, RES=10, atk_interval=1.2s, cost=21, block=3.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.nearl import make_nearl as _base_stats


DEFENDER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "nearl_holy_knight_light"
_HEAL_INTERVAL = 25.0    # seconds between each AoE heal pulse
_HEAL_RATIO = 0.08       # 8% of ally max_hp restored per pulse
_ACCUM_ATTR = "_nearl_heal_accum"

_HEAL_RANGE = {(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)}


def _on_tick(world, carrier: UnitState, dt: float) -> None:
    accum = getattr(carrier, _ACCUM_ATTR, 0.0) + dt
    if accum < _HEAL_INTERVAL:
        setattr(carrier, _ACCUM_ATTR, accum)
        return
    if carrier.position is not None:
        cx, cy = round(carrier.position[0]), round(carrier.position[1])
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp or ally.position is None:
                continue
            ax, ay = round(ally.position[0]), round(ally.position[1])
            if (ax - cx, ay - cy) in _HEAL_RANGE:
                healed = ally.heal(int(ally.max_hp * _HEAL_RATIO))
                if healed > 0:
                    world.global_state.total_healing_done += healed
                    world.log(
                        f"Nearl Holy Knight → {ally.name}  heal={healed}  ({ally.hp}/{ally.max_hp})"
                    )
    setattr(carrier, _ACCUM_ATTR, accum - _HEAL_INTERVAL)


register_talent(_TALENT_TAG, on_tick=_on_tick)


# --- S2: Justice ---
_S2_TAG = "nearl_s2_justice"
_S2_ATK_RATIO = 1.00     # ATK +100%
_S2_DEF_RATIO = 0.55     # DEF +55%
_S2_SOURCE_TAG = "nearl_s2_justice"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_SOURCE_TAG,
    ))
    world.log(f"Nearl S2 Justice — ATK +{_S2_ATK_RATIO:.0%}, DEF +{_S2_DEF_RATIO:.0%}")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SOURCE_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_nearl(slot: str = "S2") -> UnitState:
    """Nearl E2 max. Talent: 25s passive AoE heal. S2: ATK+100%/DEF+55% 30s."""
    op = _base_stats()
    op.name = "Nearl"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_RANGE
    op.cost = 21

    op.talents = [TalentComponent(name="Holy Knight's Light", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Justice",
            slot="S2",
            sp_cost=30,
            initial_sp=15,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
