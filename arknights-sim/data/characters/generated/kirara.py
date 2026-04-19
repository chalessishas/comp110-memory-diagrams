"""绮良 — generated from ArknightsGameData char_478_kirara.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_478_kirara
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kirara() -> UnitState:
    return UnitState(
        name='绮良',
        faction=Faction.ALLY,
        max_hp=1980,
        atk=858,
        defence=340,
        res=30.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=20,
        redeploy_cd=70.0,
    )
