"""异客 — generated from ArknightsGameData char_472_pasngr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_472_pasngr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pasngr() -> UnitState:
    return UnitState(
        name='异客',
        faction=Faction.ALLY,
        max_hp=1558,
        atk=774,
        defence=130,
        res=20.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=33,
        redeploy_cd=70.0,
    )
