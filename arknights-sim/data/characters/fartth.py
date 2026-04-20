"""Fartooth (远牙) — 6★ Sniper (Heavy archetype).

SNIPER_HEAVY trait: High-ATK, slow-interval physical ranged attacker.

Talent "Mark of the Hunt" (E2):
  After each physical hit, fires an arts chaser for _TALENT_ARTS_RATIO×ATK Arts
  damage to the same target. During S3, chaser ratio increases to _TALENT_ARTS_RATIO_S3.

S3 "Predator": MANUAL.
  ATK +_S3_ATK_RATIO for _S3_DURATION seconds.
  Arts chaser damage increases automatically (talent checks skill.active_remaining).
  sp_cost=50, initial_sp=25, AUTO_TIME, MANUAL trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_430_fartth):
  HP=1522, ATK=1296, DEF=163, RES=0, atk_interval=2.7s, cost=22, block=1.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape, TalentComponent,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.fartth import make_fartth as _base_stats


HEAVY_SNIPER_RANGE = RangeShape(tiles=tuple(
    (dx, dy)
    for dx in range(1, 6)
    for dy in range(-1, 2)
))

_TALENT_TAG = "fartth_mark_of_hunt"
_TALENT_ARTS_RATIO = 0.40       # arts chaser: 40% ATK normally
_TALENT_ARTS_RATIO_S3 = 0.70   # arts chaser: 70% ATK during S3
_TALENT_ARTS_TAG = "fartth_arts_chaser"

# --- S2: Aimed Shot ---
_S2_TAG = "fartth_s2_aimed_shot"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "fartth_s2_atk"
_S2_DURATION = 20.0

_S3_TAG = "fartth_s3_predator"
_S3_ATK_RATIO = 0.80
_S3_ATK_BUFF_TAG = "fartth_s3_atk"
_S3_DURATION = 20.0


def _talent_on_attack_hit(world, attacker: UnitState, target, damage: int) -> None:
    ratio = (
        _TALENT_ARTS_RATIO_S3
        if (attacker.skill is not None and attacker.skill.active_remaining > 0)
        else _TALENT_ARTS_RATIO
    )
    raw_arts = int(attacker.effective_atk * ratio)
    arts_dealt = target.take_arts(raw_arts)
    world.global_state.total_damage_dealt += arts_dealt
    world.log(f"Fartooth Mark → {target.name}  arts={arts_dealt}  ({target.hp}/{target.max_hp})")


register_talent(_TALENT_TAG, on_attack_hit=_talent_on_attack_hit)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Fartooth S2 Aimed Shot — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_fartth(slot: str = "S3") -> UnitState:
    """Fartooth E2 max. Talent: arts chaser on each hit. S3: ATK+80% + boosted arts chaser."""
    op = _base_stats()
    op.name = "Fartooth"
    op.archetype = RoleArchetype.SNIPER_HEAVY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = False
    op.range_shape = HEAVY_SNIPER_RANGE
    op.block = 1
    op.cost = 22

    op.talents = [TalentComponent(name="Mark of the Hunt", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Aimed Shot",
            slot="S2",
            sp_cost=25,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Predator",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
