"""Bison (拜松) — 5* Defender (Protector archetype).

Talent "Cross Cover" (交叉掩护): DEF +70 (flat) while deployed.

S1 "DEF Up γ" (防御力强化·γ型): DEF +100% for 40s.
  sp_cost=30, initial_sp=15, MANUAL, AUTO_TIME.

S2 "Deepen Battleline" (深化阵线): self DEF +120%, all deployed allies DEF +30%, 40s.
  sp_cost=50, initial_sp=20, MANUAL, AUTO_TIME.
  (Taunt mechanic not modeled — no taunt system in ECS.)

Base stats from ArknightsGameData (E2 max, trust 100).
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
from data.characters.generated.bison import make_bison as _base_stats


DEFENDER_MELEE = RangeShape(tiles=((0, 0),))

# --- Talent: Cross Cover ---
_TALENT_TAG = "bison_cross_cover"
_TALENT_BUFF_TAG = "bison_def_passive"
_TALENT_DEF_FLAT = 70.0


def _talent_on_deploy(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_BUFF_TAG]
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.FLAT,
        value=_TALENT_DEF_FLAT, source_tag=_TALENT_BUFF_TAG,
    ))


register_talent(_TALENT_TAG, on_deploy=_talent_on_deploy)

# --- S1: DEF Up γ ---
_S1_TAG = "bison_s1_def_up"
_S1_DEF_RATIO = 1.00
_S1_BUFF_TAG = "bison_s1_def"
_S1_DURATION = 40.0

# --- S2: Deepen Battleline ---
_S2_TAG = "bison_s2_deepen_battleline"
_S2_SELF_DEF_RATIO = 1.20
_S2_ALLY_DEF_RATIO = 0.30
_S2_SELF_BUFF_TAG = "bison_s2_self_def"
_S2_ALLY_BUFF_TAG = "bison_s2_ally_def"
_S2_DURATION = 40.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Bison S1 DEF Up γ — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_SELF_DEF_RATIO, source_tag=_S2_SELF_BUFF_TAG,
    ))
    for ally in world.allies():
        if not ally.alive or not ally.deployed or ally is carrier:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.DEF, stack=BuffStack.RATIO,
            value=_S2_ALLY_DEF_RATIO, source_tag=_S2_ALLY_BUFF_TAG,
        ))
    world.log(f"Bison S2 Deepen Battleline — self DEF+{_S2_SELF_DEF_RATIO:.0%}, allies DEF+{_S2_ALLY_DEF_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_SELF_BUFF_TAG]
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S2_ALLY_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_bison(slot: str = "S2") -> UnitState:
    """Bison E2 max. Talent: DEF+70 flat. S1: DEF+100%/40s. S2: self DEF+120% + allies DEF+30%/40s."""
    op = _base_stats()
    op.name = "Bison"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_MELEE
    op.talents = [TalentComponent(name="Cross Cover", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="DEF Up γ",
            slot="S1",
            sp_cost=30,
            initial_sp=15,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Deepen Battleline",
            slot="S2",
            sp_cost=50,
            initial_sp=20,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
