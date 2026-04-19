"""蚀清 — generated from ArknightsGameData char_489_serum.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_489_serum
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_serum() -> UnitState:
    return UnitState(
        name='蚀清',
        faction=Faction.ALLY,
        max_hp=1572,
        atk=850,
        defence=120,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=33,
        redeploy_cd=70.0,
    )
