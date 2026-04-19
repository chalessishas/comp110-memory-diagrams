"""Movement — 敌人沿路径前进（考虑减速/阻挡/控制状态）."""
from __future__ import annotations
from ..types import BuffAxis, Faction, StatusKind


def movement_system(world, dt: float) -> None:
    for u in world.units:
        if not u.alive or u.faction != Faction.ENEMY:
            continue
        if not u.deployed or not u.path:
            continue
        # 控制效果阻止移动
        if not u.can_act():
            continue
        # 被阻挡则不动
        if u.blocked_by_unit_ids:
            continue

        # 减速 + aspd buffs → movement speed pipeline
        speed = u.effective_stat(BuffAxis.MOVE_SPEED, base=u.move_speed)
        # 冻伤/减速 status 直接减 (可和 buff 叠加)
        for s in u.statuses:
            if s.kind == StatusKind.SLOW:
                speed *= 1.0 - s.params.get("amount", 0.3)
            elif s.kind == StatusKind.COLD:
                speed *= 0.7

        u.path_progress += max(0.0, speed) * dt

        # 更新浮点位置（给 AOE 索敌用）
        path_len = len(u.path) - 1
        if path_len > 0:
            p = min(u.path_progress, float(path_len))
            i = int(p)
            frac = p - i
            if i >= len(u.path) - 1:
                u.position = (float(u.path[-1][0]), float(u.path[-1][1]))
            else:
                x0, y0 = u.path[i]
                x1, y1 = u.path[i + 1]
                u.position = (x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac)
