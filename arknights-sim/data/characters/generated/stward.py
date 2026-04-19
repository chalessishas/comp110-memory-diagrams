"""史都华德 — generated from ArknightsGameData char_210_stward.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_210_stward
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_stward() -> UnitState:
    return UnitState(
        name='史都华德',
        faction=Faction.ALLY,
        max_hp=1100,
        atk=520,
        defence=90,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
