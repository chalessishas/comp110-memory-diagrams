"""波登可 — generated from ArknightsGameData char_258_podego.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_258_podego
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_podego() -> UnitState:
    return UnitState(
        name='波登可',
        faction=Faction.ALLY,
        max_hp=1163,
        atk=542,
        defence=96,
        res=20.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
