"""风丸 — generated from ArknightsGameData char_4016_kazema.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4016_kazema
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kazema() -> UnitState:
    return UnitState(
        name='风丸',
        faction=Faction.ALLY,
        max_hp=2372,
        atk=772,
        defence=318,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=15,
        redeploy_cd=70.0,
    )
