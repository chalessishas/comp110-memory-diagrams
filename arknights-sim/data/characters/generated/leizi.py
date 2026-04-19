"""惊蛰 — generated from ArknightsGameData char_306_leizi.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_306_leizi
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_leizi() -> UnitState:
    return UnitState(
        name='惊蛰',
        faction=Faction.ALLY,
        max_hp=1443,
        atk=710,
        defence=119,
        res=20.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=32,
        redeploy_cd=70.0,
    )
