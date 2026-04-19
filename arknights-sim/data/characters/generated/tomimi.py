"""特米米 — generated from ArknightsGameData char_411_tomimi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_411_tomimi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tomimi() -> UnitState:
    return UnitState(
        name='特米米',
        faction=Faction.ALLY,
        max_hp=2120,
        atk=635,
        defence=119,
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
