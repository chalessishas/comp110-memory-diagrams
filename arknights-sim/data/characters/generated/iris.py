"""爱丽丝 — generated from ArknightsGameData char_338_iris.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_338_iris
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_iris() -> UnitState:
    return UnitState(
        name='爱丽丝',
        faction=Faction.ALLY,
        max_hp=1535,
        atk=1389,
        defence=125,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
