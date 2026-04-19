"""瑕光 — generated from ArknightsGameData char_423_blemsh.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_423_blemsh
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_blemsh() -> UnitState:
    return UnitState(
        name='瑕光',
        faction=Faction.ALLY,
        max_hp=3242,
        atk=581,
        defence=601,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=22,
        redeploy_cd=70.0,
    )
