"""摆渡人 — generated from ArknightsGameData char_4166_varkis.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4166_varkis
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_varkis() -> UnitState:
    return UnitState(
        name='摆渡人',
        faction=Faction.ALLY,
        max_hp=2772,
        atk=810,
        defence=333,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=25,
        redeploy_cd=80.0,
    )
