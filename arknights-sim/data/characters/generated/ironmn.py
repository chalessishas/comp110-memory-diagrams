"""白铁 — generated from ArknightsGameData char_4072_ironmn.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4072_ironmn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ironmn() -> UnitState:
    return UnitState(
        name='白铁',
        faction=Faction.ALLY,
        max_hp=2723,
        atk=633,
        defence=461,
        res=0.0,
        atk_interval=1.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=19,
        redeploy_cd=70.0,
    )
