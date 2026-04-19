"""克洛丝 — generated from ArknightsGameData char_124_kroos.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_124_kroos
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kroos() -> UnitState:
    return UnitState(
        name='克洛丝',
        faction=Faction.ALLY,
        max_hp=1060,
        atk=425,
        defence=126,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
