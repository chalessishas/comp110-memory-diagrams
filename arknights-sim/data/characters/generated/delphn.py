"""戴菲恩 — generated from ArknightsGameData char_4110_delphn.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4110_delphn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_delphn() -> UnitState:
    return UnitState(
        name='戴菲恩',
        faction=Faction.ALLY,
        max_hp=1532,
        atk=1370,
        defence=128,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=26,
        redeploy_cd=80.0,
    )
