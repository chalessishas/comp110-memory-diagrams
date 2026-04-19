"""冬时 — generated from ArknightsGameData char_4208_wintim.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4208_wintim
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wintim() -> UnitState:
    return UnitState(
        name='冬时',
        faction=Faction.ALLY,
        max_hp=1745,
        atk=537,
        defence=270,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=35.0,
    )
