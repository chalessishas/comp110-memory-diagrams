"""引星棘刺 — generated from ArknightsGameData char_1039_thorn2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1039_thorn2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_thorn2() -> UnitState:
    return UnitState(
        name='引星棘刺',
        faction=Faction.ALLY,
        max_hp=1373,
        atk=541,
        defence=106,
        res=30.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
