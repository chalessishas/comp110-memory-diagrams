"""奎隆，摩诃萨埵权化 — generated from ArknightsGameData enemy_2099_skzfkl level 0.
motion=WALK  applyWay=MELEE  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_2099_skzfkl
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_skzfkl(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='奎隆，摩诃萨埵权化',
        faction=Faction.ENEMY,
        max_hp=250000,
        atk=3000,
        defence=1500,
        res=70.0,
        atk_interval=6.0,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
