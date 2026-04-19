"""深律 — generated from ArknightsGameData char_4109_baslin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4109_baslin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_baslin() -> UnitState:
    return UnitState(
        name='深律',
        faction=Faction.ALLY,
        max_hp=2770,
        atk=523,
        defence=600,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=21,
        redeploy_cd=70.0,
    )
