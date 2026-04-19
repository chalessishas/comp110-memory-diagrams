"""水月 — generated from ArknightsGameData char_437_mizuki.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_437_mizuki
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mizuki() -> UnitState:
    return UnitState(
        name='水月',
        faction=Faction.ALLY,
        max_hp=1758,
        atk=975,
        defence=356,
        res=30.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=21,
        redeploy_cd=70.0,
    )
