"""PhonoR-0 — generated from ArknightsGameData char_4136_phonor.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4136_phonor
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_phonor() -> UnitState:
    return UnitState(
        name='PhonoR-0',
        faction=Faction.ALLY,
        max_hp=520,
        atk=235,
        defence=30,
        res=5.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=3,
        redeploy_cd=200.0,
    )
