"""微风 — generated from ArknightsGameData char_275_breeze.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_275_breeze
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_breeze() -> UnitState:
    return UnitState(
        name='微风',
        faction=Faction.ALLY,
        max_hp=1795,
        atk=373,
        defence=153,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
