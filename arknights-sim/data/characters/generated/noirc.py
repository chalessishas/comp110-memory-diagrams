"""黑角 — generated from ArknightsGameData char_500_noirc.
Source: E0 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_500_noirc
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_noirc() -> UnitState:
    return UnitState(
        name='黑角',
        faction=Faction.ALLY,
        max_hp=1670,
        atk=240,
        defence=355,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=14,
        redeploy_cd=70.0,
    )
