"""聆音 — generated from ArknightsGameData char_4187_graceb.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4187_graceb
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_graceb() -> UnitState:
    return UnitState(
        name='聆音',
        faction=Faction.ALLY,
        max_hp=2600,
        atk=900,
        defence=350,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=22,
        redeploy_cd=70.0,
    )
