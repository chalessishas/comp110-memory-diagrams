"""华法琳 — generated from ArknightsGameData char_171_bldsk.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_171_bldsk
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bldsk() -> UnitState:
    return UnitState(
        name='华法琳',
        faction=Faction.ALLY,
        max_hp=1520,
        atk=580,
        defence=125,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
