"""缇缇 — generated from ArknightsGameData char_4056_titi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4056_titi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_titi() -> UnitState:
    return UnitState(
        name='缇缇',
        faction=Faction.ALLY,
        max_hp=1605,
        atk=598,
        defence=117,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
