"""刻俄柏 — generated from ArknightsGameData char_2013_cerber.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2013_cerber
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cerber() -> UnitState:
    return UnitState(
        name='刻俄柏',
        faction=Faction.ALLY,
        max_hp=1565,
        atk=757,
        defence=128,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
