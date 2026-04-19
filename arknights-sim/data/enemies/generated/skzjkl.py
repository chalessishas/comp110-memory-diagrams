"""奎隆，摩诃萨埵权化 — generated from ArknightsGameData enemy_2089_skzjkl level 0.
motion=WALK  applyWay=MELEE  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2089_skzjkl
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzjkl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='奎隆，摩诃萨埵权化',
        faction=Faction.ENEMY,
        max_hp=300000,
        atk=1800,
        defence=2000,
        res=75.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
