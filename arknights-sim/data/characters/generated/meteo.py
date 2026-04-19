"""陨星 — generated from ArknightsGameData char_219_meteo.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_219_meteo
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_meteo() -> UnitState:
    return UnitState(
        name='陨星',
        faction=Faction.ALLY,
        max_hp=1505,
        atk=950,
        defence=116,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=28,
        redeploy_cd=70.0,
    )
