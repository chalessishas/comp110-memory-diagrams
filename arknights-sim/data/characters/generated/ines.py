"""伊内丝 — generated from ArknightsGameData char_4087_ines.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4087_ines
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ines() -> UnitState:
    return UnitState(
        name='伊内丝',
        faction=Faction.ALLY,
        max_hp=2121,
        atk=639,
        defence=311,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=35.0,
    )
