"""SilverAsh — 6* Guard (Lord archetype).

SOURCE: PRTS wiki, E2 L90, 信赖 100, no potentials, no module.
VERIFY: replace with akgd character_table.json derived values next iteration.
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill


# Guard 分支「领主」标准远程 2-格范围：前一格 + 前后邻居（十字形）
# 实际 in-game 范围图更复杂；此处先用能覆盖 "attack tile in front" 的最小集
GUARD_LORD_RANGE = RangeShape(tiles=(
    (0, 0),          # 本格（melee block）
    (1, 0),          # 前一格（lord 的远程特性）
))


# --- S3 Truesilver Slash behavior ---
_S3_TAG = "silverash_s3_truesilver_slash"
_S3_ATK_RATIO = 1.80   # +180% at rank III
_S3_BUFF_TAG = "silverash_s3_atk_buff"


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S3_ATK_RATIO, source_tag=_S3_BUFF_TAG,
    ))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_silverash(slot: str = "S3") -> UnitState:
    """SilverAsh E2 L90. slot='S3' is the canonical 'Truesilver Slash' build."""
    op = UnitState(
        name="SilverAsh",
        faction=Faction.ALLY,
        max_hp=2671,
        atk=723,
        defence=360,
        res=10.0,
        atk_interval=1.6,
        profession=Profession.GUARD,
        archetype=RoleArchetype.GUARD_LORD,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=True,
        block=2,
        range_shape=GUARD_LORD_RANGE,
        cost=31,
        redeploy_cd=70.0,
    )
    if slot == "S3":
        op.skill = SkillComponent(
            name="Truesilver Slash",
            slot="S3",
            sp_cost=20,
            duration=15.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S3_TAG,
        )
    return op
