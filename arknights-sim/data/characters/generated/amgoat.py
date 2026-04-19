"""艾雅法拉 — generated from ArknightsGameData char_180_amgoat.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_180_amgoat
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_amgoat() -> UnitState:
    return UnitState(
        name='艾雅法拉',
        faction=Faction.ALLY,
        max_hp=1743,
        atk=735,
        defence=122,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
