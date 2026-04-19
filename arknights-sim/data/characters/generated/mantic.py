"""狮蝎 — generated from ArknightsGameData char_215_mantic.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_215_mantic
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mantic() -> UnitState:
    return UnitState(
        name='狮蝎',
        faction=Faction.ALLY,
        max_hp=1630,
        atk=871,
        defence=373,
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
