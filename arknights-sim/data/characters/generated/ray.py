"""莱伊 — generated from ArknightsGameData char_4117_ray.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4117_ray
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ray() -> UnitState:
    return UnitState(
        name='莱伊',
        faction=Faction.ALLY,
        max_hp=1933,
        atk=1192,
        defence=228,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
