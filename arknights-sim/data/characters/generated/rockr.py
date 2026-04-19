"""洛洛 — generated from ArknightsGameData char_4040_rockr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4040_rockr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rockr() -> UnitState:
    return UnitState(
        name='洛洛',
        faction=Faction.ALLY,
        max_hp=1468,
        atk=380,
        defence=123,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
