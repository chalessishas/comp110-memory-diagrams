"""苦艾 — generated from ArknightsGameData char_405_absin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_405_absin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_absin() -> UnitState:
    return UnitState(
        name='苦艾',
        faction=Faction.ALLY,
        max_hp=1420,
        atk=703,
        defence=124,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=22,
        redeploy_cd=80.0,
    )
