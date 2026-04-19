"""灵知 — generated from ArknightsGameData char_206_gnosis.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_206_gnosis
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_gnosis() -> UnitState:
    return UnitState(
        name='灵知',
        faction=Faction.ALLY,
        max_hp=2035,
        atk=535,
        defence=132,
        res=25.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
