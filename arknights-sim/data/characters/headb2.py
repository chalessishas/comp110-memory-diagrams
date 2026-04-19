"""怒潮凛冬 (Mudrock/Wild Mane character, 6* Guard — 撼地者).

Curated layer wrapping generated/headb2.py base stats + her 撼地者 特性:
attacks deal 50% ATK splash damage within 1.0 tile radius of primary target.
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import RoleArchetype
from data.characters.generated.headb2 import make_headb2 as _base_stats


def make_headb2() -> UnitState:
    op = _base_stats()
    op.archetype = RoleArchetype.GUARD_CRUSHER   # 撼地者
    # 撼地者 特性: 攻击使目标周围的其他敌人受到相当于攻击力50%的群体物理伤害
    # 溅射半径 1.0 格, 不对主目标生效 — combat_system 的 `other is target`
    # 跳过已保证不对主目标生效, 倍率 0.5 为 PRTS 特性描述
    op.splash_radius = 1.0
    op.splash_atk_multiplier = 0.5
    return op
