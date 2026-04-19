"""吉星 — generated from ArknightsGameData char_4203_kichi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4203_kichi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kichi() -> UnitState:
    return UnitState(
        name='吉星',
        faction=Faction.ALLY,
        max_hp=2310,
        atk=792,
        defence=190,
        res=0.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=31,
        redeploy_cd=70.0,
    )
