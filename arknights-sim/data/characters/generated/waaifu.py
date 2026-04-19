"""槐琥 — generated from ArknightsGameData char_243_waaifu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_243_waaifu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_waaifu() -> UnitState:
    return UnitState(
        name='槐琥',
        faction=Faction.ALLY,
        max_hp=1455,
        atk=586,
        defence=334,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=18.0,
    )
