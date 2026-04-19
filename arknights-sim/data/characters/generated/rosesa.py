"""瑰盐 — generated from ArknightsGameData char_4163_rosesa.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4163_rosesa
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rosesa() -> UnitState:
    return UnitState(
        name='瑰盐',
        faction=Faction.ALLY,
        max_hp=1875,
        atk=360,
        defence=151,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=19,
        redeploy_cd=80.0,
    )
