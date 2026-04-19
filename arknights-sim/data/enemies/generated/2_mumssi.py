"""“脚脚生风”阵地击球手 — generated from ArknightsGameData enemy_4012_mumssi_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4012_mumssi_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mumssi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“脚脚生风”阵地击球手',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=1350,
        defence=300,
        res=20.0,
        atk_interval=3.0,
        move_speed=2.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
