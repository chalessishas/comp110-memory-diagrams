"""絮雨 — generated from ArknightsGameData char_436_whispr.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_436_whispr
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_whispr() -> UnitState:
    return UnitState(
        name='絮雨',
        faction=Faction.ALLY,
        max_hp=1632,
        atk=532,
        defence=119,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
