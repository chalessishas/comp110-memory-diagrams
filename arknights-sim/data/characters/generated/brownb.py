"""猎蜂 — generated from ArknightsGameData char_137_brownb.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_137_brownb
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_brownb() -> UnitState:
    return UnitState(
        name='猎蜂',
        faction=Faction.ALLY,
        max_hp=2435,
        atk=573,
        defence=312,
        res=0.0,
        atk_interval=0.78,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=70.0,
    )
