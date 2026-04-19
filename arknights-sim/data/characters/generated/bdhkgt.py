"""截云 — generated from ArknightsGameData char_4078_bdhkgt.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4078_bdhkgt
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bdhkgt() -> UnitState:
    return UnitState(
        name='截云',
        faction=Faction.ALLY,
        max_hp=1650,
        atk=920,
        defence=115,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=30,
        redeploy_cd=80.0,
    )
