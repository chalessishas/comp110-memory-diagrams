"""Mon3tr — generated from ArknightsGameData char_4179_monstr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4179_monstr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_monstr() -> UnitState:
    return UnitState(
        name='Mon3tr',
        faction=Faction.ALLY,
        max_hp=2235,
        atk=558,
        defence=221,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
