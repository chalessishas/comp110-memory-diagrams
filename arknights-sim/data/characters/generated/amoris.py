"""祐天寺若麦 — generated from ArknightsGameData char_4185_amoris.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4185_amoris
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_amoris() -> UnitState:
    return UnitState(
        name='祐天寺若麦',
        faction=Faction.ALLY,
        max_hp=2632,
        atk=1230,
        defence=379,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=21,
        redeploy_cd=80.0,
    )
