"""怒潮凛冬 — generated from ArknightsGameData char_1051_headb2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1051_headb2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_headb2() -> UnitState:
    return UnitState(
        name='怒潮凛冬',
        faction=Faction.ALLY,
        max_hp=2950,
        atk=1312,
        defence=473,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=20,
        redeploy_cd=70.0,
    )
