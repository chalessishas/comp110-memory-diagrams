"""“力大如驮”鼷兽补给员 — generated from ArknightsGameData enemy_4005_musqrl_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4005_musqrl_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_musqrl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“力大如驮”鼷兽补给员',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1200,
        defence=800,
        res=20.0,
        atk_interval=0.8,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
