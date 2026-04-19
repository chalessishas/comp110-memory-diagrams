"""诗怀雅 — generated from ArknightsGameData char_308_swire.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_308_swire
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_swire() -> UnitState:
    return UnitState(
        name='诗怀雅',
        faction=Faction.ALLY,
        max_hp=1914,
        atk=696,
        defence=443,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=16,
        redeploy_cd=70.0,
    )
