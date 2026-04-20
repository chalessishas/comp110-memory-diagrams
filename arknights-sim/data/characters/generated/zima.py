"""吉娜 (Zima) — generated from ArknightsGameData char_219_zima.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_219_zima
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_zima() -> UnitState:
    return UnitState(
        name='吉娜',
        faction=Faction.ALLY,
        max_hp=2177,
        atk=637,
        defence=310,
        res=0.0,
        atk_interval=1.2,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=14,
        redeploy_cd=70.0,
    )
