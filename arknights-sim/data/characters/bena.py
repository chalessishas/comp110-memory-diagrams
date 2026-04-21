"""Bena (贝娜) — 5★ Specialist (Geek archetype).

SPEC_GEEK trait: Standard melee attack. Geeks trade survivability for output.

Talent "Bloodlust" (E2):
  When Bena's HP is below 50% of max, ATK is increased by _TALENT_ATK_BONUS (ratio).

S2 "Overdrive": MANUAL.
  ATK +_S2_ATK_RATIO for _S2_DURATION seconds.
  But: each tick, Bena loses _S2_HP_DRAIN_RATIO×max_HP (HP never drops below 1).
  Models the self-burning "I don't care about survival" SPEC_GEEK philosophy.
  sp_cost=45, initial_sp=20, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100, char_369_bena):
  HP=2535, ATK=742, DEF=315, RES=0, atk_interval=1.2s, cost=17, block=2.
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
from data.characters.generated.bena import make_bena as _base_stats


GEEK_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TALENT_TAG = "bena_bloodlust"
_TALENT_ATK_BONUS = 0.35     # +35% ATK when HP < 50%
_TALENT_ATK_TAG = "bena_bloodlust_atk"
_HP_LOW_THRESHOLD = 0.50

_S2_TAG = "bena_s2_overdrive"
_S2_ATK_RATIO = 0.80
_S2_ATK_BUFF_TAG = "bena_s2_atk"
_S2_HP_DRAIN_RATIO = 0.03    # 3% max HP drained per second
_S2_DURATION = 15.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    if not carrier.deployed:
        return
    hp_below_threshold = (carrier.hp < carrier.max_hp * _HP_LOW_THRESHOLD)
    has_buff = any(b.source_tag == _TALENT_ATK_TAG for b in carrier.buffs)

    if hp_below_threshold and not has_buff:
        carrier.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_TALENT_ATK_BONUS, source_tag=_TALENT_ATK_TAG,
        ))
        world.log(f"Bena Bloodlust → ATK +{_TALENT_ATK_BONUS:.0%} (HP critical)")
    elif not hp_below_threshold and has_buff:
        carrier.buffs = [b for b in carrier.buffs if b.source_tag != _TALENT_ATK_TAG]


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))


def _s2_on_tick(world, carrier: UnitState, dt: float) -> None:
    drain = int(carrier.max_hp * _S2_HP_DRAIN_RATIO * dt)
    if drain > 0:
        carrier.hp = max(1, carrier.hp - drain)


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


_S3_TAG = "bena_s3_blood_frenzy"
_S3_ATK_RATIO = 1.50
_S3_ATK_BUFF_TAG = "bena_s3_atk"
_S3_HP_DRAIN_RATIO = 0.05    # 5% max HP per second
_S3_DURATION = 20.0


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG,
    ))


def _s3_on_tick(world, carrier: UnitState, dt: float) -> None:
    drain = int(carrier.max_hp * _S3_HP_DRAIN_RATIO * dt)
    if drain > 0:
        carrier.hp = max(1, carrier.hp - drain)


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_tick=_s3_on_tick, on_end=_s3_on_end)


def make_bena(slot: str = "S2") -> UnitState:
    """Bena E2 max. Talent: ATK+35% when HP < 50%. S2: ATK+80% + HP drain 3%/s. S3: ATK+150% + drain 5%/s."""
    op = _base_stats()
    op.name = "Bena"
    op.archetype = RoleArchetype.SPEC_GEEK
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = GEEK_RANGE
    op.block = 2
    op.cost = 17

    op.talents = [TalentComponent(name="Bloodlust", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Overdrive",
            slot="S2",
            sp_cost=45,
            initial_sp=20,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Blood Frenzy",
            slot="S3",
            sp_cost=50,
            initial_sp=25,
            duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
