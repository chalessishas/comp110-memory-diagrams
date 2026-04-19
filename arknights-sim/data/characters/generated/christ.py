"""Miss.Christine — generated from ArknightsGameData char_4198_christ.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4198_christ
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_christ() -> UnitState:
    return UnitState(
        name='Miss.Christine',
        faction=Faction.ALLY,
        max_hp=1324,
        atk=640,
        defence=117,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=22,
        redeploy_cd=80.0,
    )
