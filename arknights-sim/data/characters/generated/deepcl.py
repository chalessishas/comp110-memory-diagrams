"""深海色 — generated from ArknightsGameData char_110_deepcl.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_110_deepcl
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_deepcl() -> UnitState:
    return UnitState(
        name='深海色',
        faction=Faction.ALLY,
        max_hp=1350,
        atk=403,
        defence=125,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=10,
        redeploy_cd=70.0,
    )
