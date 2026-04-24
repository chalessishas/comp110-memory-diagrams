"""Fiammetta (菲亚梅塔) — 6★ Sniper (Artilleryman).

S1 "Provocate": sp_cost=14, initial_sp=5, duration=30s, AUTO_TIME, AUTO.
  ATK+60%, Attack Range+1 (range extension not modeled).
S2 "Paenitete": sp_cost=10, initial_sp=0, instant, AUTO_TIME, MANUAL (stub).
  Complex incendiary bullet + sequential chain explosion — not modeled.
S3 "Reponite": sp_cost=19, initial_sp=0, toggle, AUTO_TIME, MANUAL (stub).
  Continuous area barrage toggle replacing normal attacks — not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.phenxi import make_phenxi as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))

_S1_TAG = "phenxi_s1_provocate"
_S1_ATK_RATIO = 0.60
_S1_BUFF_TAG = "phenxi_s1_atk"
_S1_DURATION = 30.0

_S2_TAG = "phenxi_s2"
_S2_DURATION = 0.0

_S3_TAG = "phenxi_s3"
_S3_DURATION = 9999.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Fiammetta S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s (range+1 not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_phenxi(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Fiammetta"
    op.archetype = RoleArchetype.SNIPER_ARTILLERY
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Provocate", slot="S1", sp_cost=14, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Paenitete", slot="S2", sp_cost=10, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Reponite", slot="S3", sp_cost=19, initial_sp=0,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
