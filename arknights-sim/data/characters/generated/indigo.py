"""深靛 — generated from ArknightsGameData char_469_indigo.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_469_indigo
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_indigo() -> UnitState:
    return UnitState(
        name='深靛',
        faction=Faction.ALLY,
        max_hp=1435,
        atk=1216,
        defence=117,
        res=20.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=23,
        redeploy_cd=70.0,
    )
