"""安哲拉 — generated from ArknightsGameData char_218_cuttle.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_218_cuttle
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cuttle() -> UnitState:
    return UnitState(
        name='安哲拉',
        faction=Faction.ALLY,
        max_hp=1798,
        atk=1110,
        defence=128,
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
