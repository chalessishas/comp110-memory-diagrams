"""但书 — generated from ArknightsGameData char_4032_provs.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4032_provs
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_provs() -> UnitState:
    return UnitState(
        name='但书',
        faction=Faction.ALLY,
        max_hp=1298,
        atk=578,
        defence=102,
        res=20.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
