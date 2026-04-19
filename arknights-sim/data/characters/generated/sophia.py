"""鞭刃 — generated from ArknightsGameData char_265_sophia.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_265_sophia
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sophia() -> UnitState:
    return UnitState(
        name='鞭刃',
        faction=Faction.ALLY,
        max_hp=1932,
        atk=675,
        defence=460,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=18,
        redeploy_cd=80.0,
    )
