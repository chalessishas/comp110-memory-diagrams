"""撷英调香师 — generated from ArknightsGameData char_1022_flwr2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1022_flwr2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_flwr2() -> UnitState:
    return UnitState(
        name='撷英调香师',
        faction=Faction.ALLY,
        max_hp=2095,
        atk=470,
        defence=182,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=12,
        redeploy_cd=70.0,
    )
