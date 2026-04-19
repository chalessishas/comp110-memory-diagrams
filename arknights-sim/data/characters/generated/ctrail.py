"""云迹 — generated from ArknightsGameData char_4165_ctrail.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4165_ctrail
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ctrail() -> UnitState:
    return UnitState(
        name='云迹',
        faction=Faction.ALLY,
        max_hp=2255,
        atk=727,
        defence=428,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=16,
        redeploy_cd=70.0,
    )
