"""录武官 — generated from ArknightsGameData char_4196_reckpr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4196_reckpr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_reckpr() -> UnitState:
    return UnitState(
        name='录武官',
        faction=Faction.ALLY,
        max_hp=1580,
        atk=577,
        defence=124,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
