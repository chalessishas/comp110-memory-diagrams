"""刻刀 — generated from ArknightsGameData char_301_cutter.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_301_cutter
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_cutter() -> UnitState:
    return UnitState(
        name='刻刀',
        faction=Faction.ALLY,
        max_hp=2320,
        atk=641,
        defence=325,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=21,
        redeploy_cd=70.0,
    )
