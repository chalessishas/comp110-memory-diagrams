"""刺玫 — generated from ArknightsGameData char_494_vendla.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_494_vendla
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_vendla() -> UnitState:
    return UnitState(
        name='刺玫',
        faction=Faction.ALLY,
        max_hp=1550,
        atk=580,
        defence=100,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
