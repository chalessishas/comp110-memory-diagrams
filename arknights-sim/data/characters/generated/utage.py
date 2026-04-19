"""宴 — generated from ArknightsGameData char_337_utage.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_337_utage
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_utage() -> UnitState:
    return UnitState(
        name='宴',
        faction=Faction.ALLY,
        max_hp=3444,
        atk=723,
        defence=352,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
