"""角峰 — generated from ArknightsGameData char_199_yak.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_199_yak
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_yak() -> UnitState:
    return UnitState(
        name='角峰',
        faction=Faction.ALLY,
        max_hp=3620,
        atk=375,
        defence=670,
        res=5.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=21,
        redeploy_cd=70.0,
    )
