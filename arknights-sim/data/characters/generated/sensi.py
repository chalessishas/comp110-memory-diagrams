"""森西 — generated from ArknightsGameData char_4143_sensi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4143_sensi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sensi() -> UnitState:
    return UnitState(
        name='森西',
        faction=Faction.ALLY,
        max_hp=2770,
        atk=510,
        defence=620,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=23,
        redeploy_cd=80.0,
    )
