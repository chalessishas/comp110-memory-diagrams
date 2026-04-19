"""嵯峨 — generated from ArknightsGameData char_362_saga.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_362_saga
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_saga() -> UnitState:
    return UnitState(
        name='嵯峨',
        faction=Faction.ALLY,
        max_hp=2205,
        atk=615,
        defence=372,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=14,
        redeploy_cd=70.0,
    )
