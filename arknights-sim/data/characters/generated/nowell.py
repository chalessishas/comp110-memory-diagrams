"""诺威尔 — generated from ArknightsGameData char_4173_nowell.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4173_nowell
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_nowell() -> UnitState:
    return UnitState(
        name='诺威尔',
        faction=Faction.ALLY,
        max_hp=1567,
        atk=556,
        defence=108,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
