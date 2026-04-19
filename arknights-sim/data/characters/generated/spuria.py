"""空构 — generated from ArknightsGameData char_4015_spuria.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4015_spuria
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_spuria() -> UnitState:
    return UnitState(
        name='空构',
        faction=Faction.ALLY,
        max_hp=2093,
        atk=707,
        defence=138,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
