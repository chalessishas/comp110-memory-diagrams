"""赤冬 — generated from ArknightsGameData char_475_akafyu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_475_akafyu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_akafyu() -> UnitState:
    return UnitState(
        name='赤冬',
        faction=Faction.ALLY,
        max_hp=3635,
        atk=758,
        defence=383,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=70.0,
    )
