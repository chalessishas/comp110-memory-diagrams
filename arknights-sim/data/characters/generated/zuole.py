"""左乐 — generated from ArknightsGameData char_4121_zuole.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4121_zuole
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_zuole() -> UnitState:
    return UnitState(
        name='左乐',
        faction=Faction.ALLY,
        max_hp=4198,
        atk=820,
        defence=355,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=26,
        redeploy_cd=70.0,
    )
