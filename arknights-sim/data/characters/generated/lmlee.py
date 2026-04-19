"""老鲤 — generated from ArknightsGameData char_322_lmlee.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_322_lmlee
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lmlee() -> UnitState:
    return UnitState(
        name='老鲤',
        faction=Faction.ALLY,
        max_hp=2727,
        atk=844,
        defence=465,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=25.0,
    )
