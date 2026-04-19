"""缪尔赛思 — generated from ArknightsGameData char_249_mlyss.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_249_mlyss
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mlyss() -> UnitState:
    return UnitState(
        name='缪尔赛思',
        faction=Faction.ALLY,
        max_hp=1813,
        atk=537,
        defence=157,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
