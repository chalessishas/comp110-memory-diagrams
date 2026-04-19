"""多萝西 — generated from ArknightsGameData char_4048_doroth.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4048_doroth
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_doroth() -> UnitState:
    return UnitState(
        name='多萝西',
        faction=Faction.ALLY,
        max_hp=1502,
        atk=661,
        defence=172,
        res=0.0,
        atk_interval=0.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
