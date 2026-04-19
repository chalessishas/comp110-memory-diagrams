"""九色鹿 — generated from ArknightsGameData char_4019_ncdeer.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4019_ncdeer
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ncdeer() -> UnitState:
    return UnitState(
        name='九色鹿',
        faction=Faction.ALLY,
        max_hp=2035,
        atk=478,
        defence=179,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
