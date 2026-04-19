"""集团军机动弩手 — generated from ArknightsGameData enemy_10121_uasnip level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10121_uasnip
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_uasnip(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='集团军机动弩手',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=380,
        defence=200,
        res=0.0,
        atk_interval=5.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
