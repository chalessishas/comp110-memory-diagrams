"""歌蕾蒂娅 — generated from ArknightsGameData char_474_glady.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_474_glady
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_glady() -> UnitState:
    return UnitState(
        name='歌蕾蒂娅',
        faction=Faction.ALLY,
        max_hp=2309,
        atk=851,
        defence=381,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=16,
        redeploy_cd=80.0,
    )
