"""红豆 — generated from ArknightsGameData char_290_vigna.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_290_vigna
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_vigna() -> UnitState:
    return UnitState(
        name='红豆',
        faction=Faction.ALLY,
        max_hp=1845,
        atk=618,
        defence=351,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
