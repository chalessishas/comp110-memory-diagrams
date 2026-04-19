"""安比尔 — generated from ArknightsGameData char_302_glaze.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_302_glaze
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_glaze() -> UnitState:
    return UnitState(
        name='安比尔',
        faction=Faction.ALLY,
        max_hp=1595,
        atk=1052,
        defence=122,
        res=0.0,
        atk_interval=2.7,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
