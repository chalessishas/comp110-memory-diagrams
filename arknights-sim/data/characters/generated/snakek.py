"""蛇屠箱 — generated from ArknightsGameData char_150_snakek.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_150_snakek
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_snakek() -> UnitState:
    return UnitState(
        name='蛇屠箱',
        faction=Faction.ALLY,
        max_hp=3105,
        atk=365,
        defence=765,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=21,
        redeploy_cd=70.0,
    )
