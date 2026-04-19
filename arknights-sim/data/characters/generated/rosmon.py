"""迷迭香 — generated from ArknightsGameData char_391_rosmon.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_391_rosmon
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_rosmon() -> UnitState:
    return UnitState(
        name='迷迭香',
        faction=Faction.ALLY,
        max_hp=1944,
        atk=748,
        defence=275,
        res=15.0,
        atk_interval=2.1,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=70.0,
    )
