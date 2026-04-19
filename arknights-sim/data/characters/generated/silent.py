"""赫默 — generated from ArknightsGameData char_108_silent.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_108_silent
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_silent() -> UnitState:
    return UnitState(
        name='赫默',
        faction=Faction.ALLY,
        max_hp=1595,
        atk=557,
        defence=142,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
