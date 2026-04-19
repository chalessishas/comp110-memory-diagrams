"""杏仁 — generated from ArknightsGameData char_4105_almond.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4105_almond
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_almond() -> UnitState:
    return UnitState(
        name='杏仁',
        faction=Faction.ALLY,
        max_hp=2330,
        atk=695,
        defence=455,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=13,
        redeploy_cd=70.0,
    )
