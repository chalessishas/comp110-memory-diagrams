"""安洁莉娜 — generated from ArknightsGameData char_291_aglina.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_291_aglina
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_angelina() -> UnitState:
    return UnitState(
        name='安洁莉娜',
        faction=Faction.ALLY,
        max_hp=1385,
        atk=617,
        defence=120,
        res=25.0,
        atk_interval=1.9,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=14,
        redeploy_cd=70.0,
    )
