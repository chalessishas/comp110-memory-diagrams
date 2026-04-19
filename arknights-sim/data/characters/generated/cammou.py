"""卡达 — generated from ArknightsGameData char_328_cammou.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_328_cammou
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cammou() -> UnitState:
    return UnitState(
        name='卡达',
        faction=Faction.ALLY,
        max_hp=1440,
        atk=375,
        defence=120,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
