"""守林人 — generated from ArknightsGameData char_158_milu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_158_milu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_milu() -> UnitState:
    return UnitState(
        name='守林人',
        faction=Faction.ALLY,
        max_hp=1450,
        atk=1175,
        defence=131,
        res=0.0,
        atk_interval=2.7,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
