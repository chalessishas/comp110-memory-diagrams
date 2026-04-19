"""安德切尔 — generated from ArknightsGameData char_211_adnach.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_211_adnach
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_adnach() -> UnitState:
    return UnitState(
        name='安德切尔',
        faction=Faction.ALLY,
        max_hp=1080,
        atk=415,
        defence=134,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
