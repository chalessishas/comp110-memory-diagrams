"""溯光星源 — generated from ArknightsGameData char_1047_halo2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1047_halo2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_halo2() -> UnitState:
    return UnitState(
        name='溯光星源',
        faction=Faction.ALLY,
        max_hp=1420,
        atk=608,
        defence=125,
        res=25.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=18,
        redeploy_cd=80.0,
    )
