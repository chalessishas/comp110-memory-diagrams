"""TileState — 每格地块的静态类型 + 运行时状态.

静态：type (ground/elevated/goal/...)
运行时：占用者 + 效果区（如 Mudrock 地裂、Saria 祝福环、陷阱）
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from ..types import TileType


@dataclass
class TileEffect:
    """地块效果——例如 Mudrock S3 砸出来的伤害区、或 Saileach S2 的 DP 增益环."""
    kind: str                               # e.g. "damage_zone" / "dp_aura" / "trap"
    source_unit_id: Optional[int] = None    # 施加者
    expires_at: float = float("inf")        # game time
    params: Dict[str, float] = field(default_factory=dict)


@dataclass
class TileState:
    x: int
    y: int
    type: TileType
    effects: List[TileEffect] = field(default_factory=list)
    occupant_unit_id: Optional[int] = None  # 干员部署占位（单格一位）

    @property
    def is_deployable_melee(self) -> bool:
        return self.type == TileType.GROUND and self.occupant_unit_id is None

    @property
    def is_deployable_ranged(self) -> bool:
        return self.type == TileType.ELEVATED and self.occupant_unit_id is None

    @property
    def is_walkable(self) -> bool:
        return self.type in (TileType.GROUND, TileType.GOAL)


@dataclass
class TileGrid:
    """运行时地图——二维 TileState 数组 + 高层查询 helper."""
    width: int
    height: int
    tiles: Dict[Tuple[int, int], TileState] = field(default_factory=dict)

    def get(self, x: int, y: int) -> Optional[TileState]:
        return self.tiles.get((x, y))

    def set_tile(self, tile: TileState) -> None:
        self.tiles[(tile.x, tile.y)] = tile

    def iter_tiles(self):
        return self.tiles.values()

    def adjacent_tiles(self, x: int, y: int, diagonal: bool = False) -> List[TileState]:
        """4-邻居（默认）或 8-邻居。用于"高台扩散"这类天赋."""
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonal:
            offsets += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        out: List[TileState] = []
        for dx, dy in offsets:
            t = self.get(x + dx, y + dy)
            if t is not None:
                out.append(t)
        return out

    def tiles_in_euclidean_radius(self, cx: float, cy: float, radius: float) -> List[TileState]:
        r2 = radius * radius
        out: List[TileState] = []
        for t in self.tiles.values():
            dx = t.x - cx
            dy = t.y - cy
            if dx * dx + dy * dy <= r2:
                out.append(t)
        return out
