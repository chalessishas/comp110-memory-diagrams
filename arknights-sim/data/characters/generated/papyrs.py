"""莎草 — generated from ArknightsGameData char_4139_papyrs.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4139_papyrs
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_papyrs() -> UnitState:
    return UnitState(
        name='莎草',
        faction=Faction.ALLY,
        max_hp=1865,
        atk=500,
        defence=160,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=20,
        redeploy_cd=80.0,
    )
