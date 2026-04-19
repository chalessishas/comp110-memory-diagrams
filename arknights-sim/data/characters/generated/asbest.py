"""石棉 — generated from ArknightsGameData char_378_asbest.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_378_asbest
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_asbest() -> UnitState:
    return UnitState(
        name='石棉',
        faction=Faction.ALLY,
        max_hp=3135,
        atk=673,
        defence=595,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.ARTS,
        block=3,
        cost=25,
        redeploy_cd=70.0,
    )
