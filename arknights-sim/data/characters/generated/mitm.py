"""渡桥 — generated from ArknightsGameData char_4147_mitm.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4147_mitm
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mitm() -> UnitState:
    return UnitState(
        name='渡桥',
        faction=Faction.ALLY,
        max_hp=1370,
        atk=555,
        defence=122,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
