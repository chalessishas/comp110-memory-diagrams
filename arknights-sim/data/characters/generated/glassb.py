"""真理 — generated from ArknightsGameData char_195_glassb.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_195_glassb
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_glassb() -> UnitState:
    return UnitState(
        name='真理',
        faction=Faction.ALLY,
        max_hp=1280,
        atk=583,
        defence=104,
        res=20.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
