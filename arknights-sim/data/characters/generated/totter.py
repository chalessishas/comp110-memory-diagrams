"""铅踝 — generated from ArknightsGameData char_4062_totter.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4062_totter
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_totter() -> UnitState:
    return UnitState(
        name='铅踝',
        faction=Faction.ALLY,
        max_hp=1550,
        atk=970,
        defence=145,
        res=0.0,
        atk_interval=2.4,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=22,
        redeploy_cd=70.0,
    )
