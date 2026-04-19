"""煌 — generated from ArknightsGameData char_017_huang.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_017_huang
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_huang() -> UnitState:
    return UnitState(
        name='煌',
        faction=Faction.ALLY,
        max_hp=2821,
        atk=825,
        defence=415,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=24,
        redeploy_cd=70.0,
    )
