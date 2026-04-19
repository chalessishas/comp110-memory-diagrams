"""埃拉托 — generated from ArknightsGameData char_4043_erato.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4043_erato
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_erato() -> UnitState:
    return UnitState(
        name='埃拉托',
        faction=Faction.ALLY,
        max_hp=1798,
        atk=1027,
        defence=125,
        res=0.0,
        atk_interval=2.4,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=23,
        redeploy_cd=70.0,
    )
