"""亚叶 — generated from ArknightsGameData char_345_folnic.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_345_folnic
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_folnic() -> UnitState:
    return UnitState(
        name='亚叶',
        faction=Faction.ALLY,
        max_hp=1785,
        atk=529,
        defence=133,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=21,
        redeploy_cd=80.0,
    )
