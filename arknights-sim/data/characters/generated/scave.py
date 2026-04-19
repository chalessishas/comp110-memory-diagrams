"""清道夫 — generated from ArknightsGameData char_149_scave.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_149_scave
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_scave() -> UnitState:
    return UnitState(
        name='清道夫',
        faction=Faction.ALLY,
        max_hp=1835,
        atk=530,
        defence=310,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=12,
        redeploy_cd=70.0,
    )
