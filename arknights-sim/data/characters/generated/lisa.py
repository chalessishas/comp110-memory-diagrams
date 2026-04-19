"""铃兰 — generated from ArknightsGameData char_358_lisa.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_358_lisa
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lisa() -> UnitState:
    return UnitState(
        name='铃兰',
        faction=Faction.ALLY,
        max_hp=1480,
        atk=596,
        defence=128,
        res=25.0,
        atk_interval=1.9,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SUPPORTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=16,
        redeploy_cd=70.0,
    )
