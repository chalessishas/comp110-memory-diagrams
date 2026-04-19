"""松桐 — generated from ArknightsGameData char_4199_makiri.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4199_makiri
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_makiri() -> UnitState:
    return UnitState(
        name='松桐',
        faction=Faction.ALLY,
        max_hp=2002,
        atk=650,
        defence=420,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=14,
        redeploy_cd=80.0,
    )
