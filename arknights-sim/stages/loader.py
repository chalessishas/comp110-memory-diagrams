from __future__ import annotations
import yaml
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple
from core.enemy import Enemy
from core.map import Map, Tile
from core.battle import Battle, SpawnEvent
from core.operator import Operator


@dataclass
class EnemySpec:
    enemy_id: str
    count: int
    interval: float       # seconds between spawns
    path: List[Tuple[int, int]]


@dataclass
class Stage:
    id: str
    name: str
    map: Map
    enemy_specs: List[EnemySpec]
    max_lives: int = 3


# Registry of enemy constructors. Path is injected at spawn time.
_ENEMY_REGISTRY: Dict[str, Callable[[List[Tuple[int, int]]], Enemy]] = {
    "originium_slug": lambda path: Enemy(
        name="Originium Slug",
        max_hp=1300, atk=280, defence=0, res=0,
        atk_interval=1.5, attack_type="physical",
        path=path, speed=1.0,
    ),
}


def load_stage(yaml_path: str) -> Stage:
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    tiles = [Tile(t["x"], t["y"], t["type"]) for t in data["map"]["tiles"]]
    map_ = Map(width=data["map"]["width"], height=data["map"]["height"], tiles=tiles)

    specs = []
    for e in data["enemies"]:
        path = [(p[0], p[1]) for p in e["path"]]
        specs.append(EnemySpec(
            enemy_id=e["id"],
            count=e["count"],
            interval=float(e["interval"]),
            path=path,
        ))

    return Stage(
        id=data["id"],
        name=data["name"],
        map=map_,
        enemy_specs=specs,
        max_lives=int(data.get("max_lives", 3)),
    )


def stage_to_battle(stage: Stage, operators: List[Operator]) -> Battle:
    """Build a Battle from a Stage spec with wave-spawned enemies."""
    factory = _ENEMY_REGISTRY
    spawn_events: List[SpawnEvent] = []

    for spec in stage.enemy_specs:
        constructor = factory.get(spec.enemy_id)
        if constructor is None:
            raise ValueError(f"Unknown enemy id: {spec.enemy_id!r}")
        for i in range(spec.count):
            spawn_time = spec.interval * i
            enemy = constructor(spec.path)
            spawn_events.append(SpawnEvent(time=spawn_time, enemy=enemy))

    return Battle(
        operators=operators,
        enemies=[],
        max_lives=stage.max_lives,
        spawn_queue=spawn_events,
    )
