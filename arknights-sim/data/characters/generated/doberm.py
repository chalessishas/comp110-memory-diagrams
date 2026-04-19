"""杜宾 — generated from ArknightsGameData char_130_doberm.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_130_doberm
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_doberm() -> UnitState:
    return UnitState(
        name='杜宾',
        faction=Faction.ALLY,
        max_hp=2024,
        atk=632,
        defence=412,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=15,
        redeploy_cd=70.0,
    )
