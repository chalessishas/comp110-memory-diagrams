"""白金 — generated from ArknightsGameData char_204_platnm.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_204_platnm
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_platnm() -> UnitState:
    return UnitState(
        name='白金',
        faction=Faction.ALLY,
        max_hp=1550,
        atk=580,
        defence=165,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
