"""仇白 — generated from ArknightsGameData char_4082_qiubai.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4082_qiubai
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_qiubai() -> UnitState:
    return UnitState(
        name='仇白',
        faction=Faction.ALLY,
        max_hp=2480,
        atk=768,
        defence=452,
        res=10.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=20,
        redeploy_cd=70.0,
    )
