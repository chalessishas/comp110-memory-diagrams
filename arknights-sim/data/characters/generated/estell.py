"""艾丝黛尔 — generated from ArknightsGameData char_127_estell.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_127_estell
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_estell() -> UnitState:
    return UnitState(
        name='艾丝黛尔',
        faction=Faction.ALLY,
        max_hp=2850,
        atk=690,
        defence=315,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=22,
        redeploy_cd=70.0,
    )
