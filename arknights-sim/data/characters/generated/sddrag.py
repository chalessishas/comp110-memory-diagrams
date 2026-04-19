"""苇草 — generated from ArknightsGameData char_261_sddrag.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_261_sddrag
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_sddrag() -> UnitState:
    return UnitState(
        name='苇草',
        faction=Faction.ALLY,
        max_hp=2215,
        atk=632,
        defence=364,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
