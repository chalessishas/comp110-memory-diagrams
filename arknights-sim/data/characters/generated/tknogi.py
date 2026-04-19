"""月禾 — generated from ArknightsGameData char_343_tknogi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_343_tknogi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tknogi() -> UnitState:
    return UnitState(
        name='月禾',
        faction=Faction.ALLY,
        max_hp=2020,
        atk=485,
        defence=175,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
