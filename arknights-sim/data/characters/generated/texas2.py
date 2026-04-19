"""缄默德克萨斯 — generated from ArknightsGameData char_1028_texas2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1028_texas2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_texas2() -> UnitState:
    return UnitState(
        name='缄默德克萨斯',
        faction=Faction.ALLY,
        max_hp=1598,
        atk=659,
        defence=320,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=10,
        redeploy_cd=18.0,
    )
