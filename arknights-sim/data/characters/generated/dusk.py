"""夕 — generated from ArknightsGameData char_2015_dusk.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2015_dusk
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_dusk() -> UnitState:
    return UnitState(
        name='夕',
        faction=Faction.ALLY,
        max_hp=1801,
        atk=1028,
        defence=127,
        res=20.0,
        atk_interval=2.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=34,
        redeploy_cd=70.0,
    )
