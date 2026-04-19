"""安赛尔 — generated from ArknightsGameData char_212_ansel.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_212_ansel
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ansel() -> UnitState:
    return UnitState(
        name='安赛尔',
        faction=Faction.ALLY,
        max_hp=1135,
        atk=407,
        defence=109,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
