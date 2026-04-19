"""莫斯提马 — generated from ArknightsGameData char_213_mostma.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_213_mostma
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mostma() -> UnitState:
    return UnitState(
        name='莫斯提马',
        faction=Faction.ALLY,
        max_hp=1831,
        atk=939,
        defence=132,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=34,
        redeploy_cd=70.0,
    )
