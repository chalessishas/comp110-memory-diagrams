"""Originium Slug (源石虫) — Normal level 0."""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_originium_slug(path: List[Tuple[int, int]] | None = None) -> UnitState:
    """Lv 0 Originium Slug. PRTS normal data:
    HP ~1300, ATK ~280, DEF 0, RES 0, atk_interval 1.5s, move 1.0.
    """
    e = UnitState(
        name="Originium Slug",
        faction=Faction.ENEMY,
        max_hp=1300,
        atk=280,
        defence=0,
        res=0.0,
        atk_interval=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        block=0,
        move_speed=1.0,
        path=list(path) if path else [],
        deployed=True,  # enemies are "deployed" when they enter the stage
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
