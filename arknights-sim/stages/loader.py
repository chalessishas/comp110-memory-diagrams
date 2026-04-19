"""Stage YAML loader for v2 architecture.

A stage file declares:
    - map tiles (static terrain)
    - enemy waves (id + count + interval + path)
    - max_lives

The loader:
    1. Reads the YAML into StageSpec
    2. Builds a World with a TileGrid populated from map tiles
    3. Schedules spawn events onto the world's EventQueue — one per enemy,
       firing at wave.interval * wave_index seconds
"""
from __future__ import annotations
import yaml
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from core.state.global_state import GlobalState
from core.state.tile_state import TileGrid, TileState
from core.state.unit_state import UnitState
from core.systems import register_default_systems
from core.systems.spawn_system import register_spawn_handler
from core.types import TileType
from core.world import World
from data.enemies.registry import get_enemy, has_enemy, enemy_count


# --------------------------------------------------------------------------
# Enemy registry alias — YAML "id" resolves via data.enemies.registry
# which merges data/enemies/*.py (curated) + data/enemies/generated/*.py (akgd)
# --------------------------------------------------------------------------
def _enemy_factory(enemy_id: str) -> Callable[..., UnitState]:
    """Return a path-aware factory for the given enemy id."""
    if not has_enemy(enemy_id):
        raise ValueError(
            f"Unknown enemy id {enemy_id!r}. Registry has {enemy_count()} enemies."
        )
    def _build(path):
        return get_enemy(enemy_id, path=path)
    _build.__name__ = f"_enemy_factory_{enemy_id}"
    return _build


# --------------------------------------------------------------------------
# Tile type mapping — v1 YAML uses "deployment_melee" etc. as tile types; we
# map each to a v2 TileType (deployment tiles are ground tiles; profession
# restrictions are enforced by the deploy system, not the tile type).
# --------------------------------------------------------------------------
TILE_TYPE_MAP: Dict[str, TileType] = {
    "ground":            TileType.GROUND,
    "deployment_melee":  TileType.GROUND,
    "deployment_ranged": TileType.ELEVATED,
    "elevated":          TileType.ELEVATED,
    "goal":              TileType.GOAL,
    "blocked":           TileType.BLOCKED,
    "hole":              TileType.HOLE,
}


# --------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------

@dataclass
class EnemyWave:
    enemy_id: str
    count: int
    interval: float
    path: List[Tuple[int, int]]
    first_delay: float = 0.0   # offset for this wave's first spawn


@dataclass
class StageSpec:
    id: str
    name: str
    width: int
    height: int
    tiles: List[Tuple[int, int, TileType]] = field(default_factory=list)
    waves: List[EnemyWave] = field(default_factory=list)
    max_lives: int = 3
    starting_dp: int = 10


# --------------------------------------------------------------------------
# YAML -> StageSpec
# --------------------------------------------------------------------------

def load_stage(yaml_path: str) -> StageSpec:
    with open(yaml_path) as f:
        raw = yaml.safe_load(f)

    tiles: List[Tuple[int, int, TileType]] = []
    for t in raw["map"]["tiles"]:
        tile_type = TILE_TYPE_MAP.get(t["type"])
        if tile_type is None:
            raise ValueError(f"Unknown tile type {t['type']!r} in stage {raw['id']}")
        tiles.append((t["x"], t["y"], tile_type))

    waves: List[EnemyWave] = []
    for e in raw["enemies"]:
        path = [(p[0], p[1]) for p in e["path"]]
        waves.append(EnemyWave(
            enemy_id=e["id"],
            count=int(e["count"]),
            interval=float(e["interval"]),
            path=path,
            first_delay=float(e.get("first_delay", 0.0)),
        ))

    return StageSpec(
        id=raw["id"],
        name=raw["name"],
        width=int(raw["map"]["width"]),
        height=int(raw["map"]["height"]),
        tiles=tiles,
        waves=waves,
        max_lives=int(raw.get("max_lives", 3)),
        starting_dp=int(raw.get("starting_dp", 10)),
    )


# --------------------------------------------------------------------------
# StageSpec -> World (populated, systems + handlers registered, spawns scheduled)
# --------------------------------------------------------------------------

def build_world(stage: StageSpec) -> World:
    grid = TileGrid(width=stage.width, height=stage.height)
    for x, y, tile_type in stage.tiles:
        grid.set_tile(TileState(x=x, y=y, type=tile_type))

    gs = GlobalState(
        max_lives=stage.max_lives,
        lives=stage.max_lives,
        dp=stage.starting_dp,
    )
    world = World(tile_grid=grid, global_state=gs)

    register_default_systems(world)
    register_spawn_handler(world)

    # Schedule spawn events
    for wave in stage.waves:
        factory = _enemy_factory(wave.enemy_id)
        for i in range(wave.count):
            fire_at = wave.first_delay + wave.interval * i
            world.event_queue.schedule(
                fire_at=fire_at,
                kind="spawn",
                factory=factory,
                path=list(wave.path),
            )

    return world


def load_and_build(yaml_path: str) -> Tuple[StageSpec, World]:
    stage = load_stage(yaml_path)
    world = build_world(stage)
    return stage, world
