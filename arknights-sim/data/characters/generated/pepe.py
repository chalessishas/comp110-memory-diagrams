"""佩佩 — generated from ArknightsGameData char_4058_pepe.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4058_pepe
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pepe() -> UnitState:
    return UnitState(
        name='佩佩',
        faction=Faction.ALLY,
        max_hp=2851,
        atk=1360,
        defence=432,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=20,
        redeploy_cd=70.0,
    )
