"""豆苗 — generated from ArknightsGameData char_452_bstalk.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_452_bstalk
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_bstalk() -> UnitState:
    return UnitState(
        name='豆苗',
        faction=Faction.ALLY,
        max_hp=1569,
        atk=455,
        defence=125,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
