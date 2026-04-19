"""特克诺 — generated from ArknightsGameData char_4164_tecno.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4164_tecno
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tecno() -> UnitState:
    return UnitState(
        name='特克诺',
        faction=Faction.ALLY,
        max_hp=1855,
        atk=519,
        defence=105,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=20,
        redeploy_cd=70.0,
    )
