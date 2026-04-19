"""SilverAsh — 6* Guard (Lord archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Skill behaviour hand-authored here; regenerate base via:
  python tools/gen_characters.py char_172_svrash
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
from data.characters.generated.silverash import make_silverash as _base_stats


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
    # Truesilver Slash: 3 rapid strikes to all enemies in range (uses boosted ATK)
    if carrier.position is None:
        return
    ox, oy = carrier.position
    shape = carrier.range_shape
    tiles = set(shape.tiles) | set(shape.extended_tiles)
    targets = [
        e for e in world.enemies()
        if e.alive and e.position is not None
        and (round(e.position[0]) - round(ox), round(e.position[1]) - round(oy)) in tiles
    ]
    for strike in range(3):
        for t in targets:
            if not t.alive:
                continue
            dmg = t.take_physical(carrier.effective_atk)
            world.global_state.total_damage_dealt += dmg
            world.log(
                f"SilverAsh S3 strike {strike + 1}/3 → {t.name}  "
                f"dmg={dmg}  ({t.hp}/{t.max_hp})"
            )


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_BUFF_TAG]


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_silverash(slot: str = "S3") -> UnitState:
    """SilverAsh E2 max, trust 100. Base stats from akgd; S3 skill hand-authored."""
    op = _base_stats()
    op.name = "SilverAsh"
    op.archetype = RoleArchetype.GUARD_LORD
    op.range_shape = GUARD_LORD_RANGE
    op.cost = 31
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
