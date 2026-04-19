"""“碎铳之簧” — generated from ArknightsGameData enemy_9019_actrpb level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9019_actrpb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_actrpb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“碎铳之簧”',
        faction=Faction.ENEMY,
        max_hp=2500000,
        atk=600,
        defence=1100,
        res=60.0,
        atk_interval=4.5,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
