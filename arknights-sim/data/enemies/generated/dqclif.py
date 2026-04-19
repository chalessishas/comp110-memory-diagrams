"""蟹蟹爷爷 — generated from ArknightsGameData enemy_15033_dqclif level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15033_dqclif
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqclif(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='蟹蟹爷爷',
        faction=Faction.ENEMY,
        max_hp=17000,
        atk=1300,
        defence=2500,
        res=90.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
