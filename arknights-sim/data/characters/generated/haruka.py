"""遥 — generated from ArknightsGameData char_4202_haruka.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4202_haruka
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_haruka() -> UnitState:
    return UnitState(
        name='遥',
        faction=Faction.ALLY,
        max_hp=2237,
        atk=535,
        defence=178,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
