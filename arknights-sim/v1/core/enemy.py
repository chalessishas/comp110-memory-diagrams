from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from .entity import Entity


@dataclass
class Enemy(Entity):
    """An enemy unit that attacks the operator blocking it."""
    attack_type: str = "physical"  # "physical" | "magic"
    path: List[Tuple[int, int]] = field(default_factory=list)
    speed: float = 1.0  # tiles per second

    is_invisible: bool = False   # True = cannot be targeted by ranged without true sight
    is_aerial: bool = False      # True = cannot be physically blocked by melee operators

    _path_progress: float = field(init=False, default=0.0)

    def advance(self, dt: float) -> bool:
        """Move along path by dt seconds. Returns True when goal reached."""
        if not self.path:
            return False
        path_len = len(self.path) - 1
        if path_len <= 0:
            return True
        self._path_progress += self.speed * dt
        return self._path_progress >= path_len

    @property
    def tile_pos(self) -> Optional[Tuple[int, int]]:
        """Current grid tile, snapped to nearest integer path index."""
        if not self.path:
            return None
        idx = min(int(self._path_progress), len(self.path) - 1)
        return self.path[idx]

    @property
    def at_goal(self) -> bool:
        if not self.path:
            return False
        path_len = len(self.path) - 1
        return path_len <= 0 or self._path_progress >= path_len

    def attack(self, target: Entity) -> int:
        if self.attack_type == "physical":
            return target.take_physical(self.atk)
        elif self.attack_type == "magic":
            return target.take_magic(self.atk)
        raise ValueError(f"Unknown attack_type: {self.attack_type}")
