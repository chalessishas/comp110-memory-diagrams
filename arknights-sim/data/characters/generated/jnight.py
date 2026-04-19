"""正义骑士号 — generated from ArknightsGameData char_4000_jnight.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4000_jnight
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_jnight() -> UnitState:
    return UnitState(
        name='正义骑士号',
        faction=Faction.ALLY,
        max_hp=595,
        atk=217,
        defence=41,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
