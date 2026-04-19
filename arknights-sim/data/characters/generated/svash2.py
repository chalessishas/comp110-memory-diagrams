"""凛御银灰 — generated from ArknightsGameData char_1045_svash2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1045_svash2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_svash2() -> UnitState:
    return UnitState(
        name='凛御银灰',
        faction=Faction.ALLY,
        max_hp=2318,
        atk=653,
        defence=437,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=13,
        redeploy_cd=70.0,
    )
