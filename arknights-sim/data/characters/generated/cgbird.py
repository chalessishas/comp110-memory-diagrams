"""夜莺 — generated from ArknightsGameData char_179_cgbird.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_179_cgbird
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cgbird() -> UnitState:
    return UnitState(
        name='夜莺',
        faction=Faction.ALLY,
        max_hp=1705,
        atk=420,
        defence=169,
        res=5.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
