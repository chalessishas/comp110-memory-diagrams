"""断崖 — generated from ArknightsGameData char_294_ayer.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_294_ayer
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ayer() -> UnitState:
    return UnitState(
        name='断崖',
        faction=Faction.ALLY,
        max_hp=2420,
        atk=745,
        defence=375,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=19,
        redeploy_cd=70.0,
    )
