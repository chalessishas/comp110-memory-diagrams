"""砾 — generated from ArknightsGameData char_237_gravel.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_237_gravel
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_gravel() -> UnitState:
    return UnitState(
        name='砾',
        faction=Faction.ALLY,
        max_hp=1720,
        atk=452,
        defence=335,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=8,
        redeploy_cd=18.0,
    )
