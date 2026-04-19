"""羽毛笔 — generated from ArknightsGameData char_421_crow.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_421_crow
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_crow() -> UnitState:
    return UnitState(
        name='羽毛笔',
        faction=Faction.ALLY,
        max_hp=2250,
        atk=725,
        defence=452,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=22,
        redeploy_cd=70.0,
    )
