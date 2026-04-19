"""战车 — generated from ArknightsGameData char_459_tachak.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_459_tachak
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_tachak() -> UnitState:
    return UnitState(
        name='战车',
        faction=Faction.ALLY,
        max_hp=2626,
        atk=661,
        defence=349,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=24,
        redeploy_cd=80.0,
    )
