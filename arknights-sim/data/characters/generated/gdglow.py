"""澄闪 — generated from ArknightsGameData char_377_gdglow.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_377_gdglow
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_gdglow() -> UnitState:
    return UnitState(
        name='澄闪',
        faction=Faction.ALLY,
        max_hp=1480,
        atk=391,
        defence=125,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=22,
        redeploy_cd=70.0,
    )
