"""杰西卡 — generated from ArknightsGameData char_235_jesica.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_235_jesica
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_jesica() -> UnitState:
    return UnitState(
        name='杰西卡',
        faction=Faction.ALLY,
        max_hp=1320,
        atk=540,
        defence=154,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
