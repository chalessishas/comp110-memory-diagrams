"""弑君者 — generated from ArknightsGameData char_1502_crosly.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1502_crosly
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_crosly() -> UnitState:
    return UnitState(
        name='弑君者',
        faction=Faction.ALLY,
        max_hp=1695,
        atk=635,
        defence=325,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=22.0,
    )
