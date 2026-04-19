"""明椒 — generated from ArknightsGameData char_4071_peper.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4071_peper
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_peper() -> UnitState:
    return UnitState(
        name='明椒',
        faction=Faction.ALLY,
        max_hp=1866,
        atk=489,
        defence=171,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
