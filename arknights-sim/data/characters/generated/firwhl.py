"""火哨 — generated from ArknightsGameData char_493_firwhl.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_493_firwhl
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_firwhl() -> UnitState:
    return UnitState(
        name='火哨',
        faction=Faction.ALLY,
        max_hp=2983,
        atk=932,
        defence=618,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=27,
        redeploy_cd=70.0,
    )
