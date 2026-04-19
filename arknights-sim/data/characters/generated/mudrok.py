"""泥岩 — generated from ArknightsGameData char_311_mudrok.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_311_mudrok
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mudrok() -> UnitState:
    return UnitState(
        name='泥岩',
        faction=Faction.ALLY,
        max_hp=4428,
        atk=882,
        defence=662,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=36,
        redeploy_cd=70.0,
    )
