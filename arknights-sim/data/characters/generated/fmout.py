"""远山 — generated from ArknightsGameData char_109_fmout.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_109_fmout
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_fmout() -> UnitState:
    return UnitState(
        name='远山',
        faction=Faction.ALLY,
        max_hp=1598,
        atk=785,
        defence=118,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
