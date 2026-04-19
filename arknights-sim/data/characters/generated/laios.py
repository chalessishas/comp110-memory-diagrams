"""莱欧斯 — generated from ArknightsGameData char_4142_laios.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4142_laios
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_laios() -> UnitState:
    return UnitState(
        name='莱欧斯',
        faction=Faction.ALLY,
        max_hp=3868,
        atk=975,
        defence=281,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
