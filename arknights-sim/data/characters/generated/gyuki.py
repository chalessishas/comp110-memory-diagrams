"""缠丸 — generated from ArknightsGameData char_289_gyuki.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_289_gyuki
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_gyuki() -> UnitState:
    return UnitState(
        name='缠丸',
        faction=Faction.ALLY,
        max_hp=4090,
        atk=916,
        defence=156,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
