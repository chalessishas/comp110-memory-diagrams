"""Spawn event handler — registered to EventQueue at kind='spawn'.

Payload contract:
    factory: Callable[[list[tuple[int,int]]], UnitState]  # enemy factory
    path:    list[tuple[int,int]]                         # path for this instance
"""
from __future__ import annotations
from typing import Any


def spawn_handler(world, event) -> None:
    factory = event.payload["factory"]
    path = event.payload["path"]
    unit = factory(path=path)
    world.add_unit(unit)
    world.log(f"{unit.name} enters the battlefield")


def register_spawn_handler(world) -> None:
    """Install the default spawn handler on this world's EventQueue."""
    world.event_queue.register("spawn", spawn_handler)
