"""黍 — generated from ArknightsGameData char_2025_shu.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2025_shu
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_shu() -> UnitState:
    return UnitState(
        name='黍',
        faction=Faction.ALLY,
        max_hp=3213,
        atk=529,
        defence=662,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=22,
        redeploy_cd=70.0,
    )
