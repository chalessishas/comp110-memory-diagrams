from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Tile:
    x: int
    y: int
    type: str  # ground | elevated | goal | deployment_melee | deployment_ranged
    terrain_effect: str = ""  # "" | "icy" | "oil"


@dataclass
class Map:
    width: int
    height: int
    tiles: List[Tile] = field(default_factory=list)

    def goal_positions(self) -> List[Tuple[int, int]]:
        return [(t.x, t.y) for t in self.tiles if t.type == "goal"]

    def melee_deploy_positions(self) -> List[Tuple[int, int]]:
        return [(t.x, t.y) for t in self.tiles
                if t.type in ("ground", "deployment_melee")]

    def ranged_deploy_positions(self) -> List[Tuple[int, int]]:
        return [(t.x, t.y) for t in self.tiles
                if t.type in ("elevated", "deployment_ranged")]
