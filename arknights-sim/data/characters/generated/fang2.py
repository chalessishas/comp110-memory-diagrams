"""历阵锐枪芬 — generated from ArknightsGameData char_1036_fang2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1036_fang2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_fang2() -> UnitState:
    return UnitState(
        name='历阵锐枪芬',
        faction=Faction.ALLY,
        max_hp=2226,
        atk=640,
        defence=360,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
