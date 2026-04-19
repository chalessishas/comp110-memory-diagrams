"""斥罪 — generated from ArknightsGameData char_4065_judge.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4065_judge
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_judge() -> UnitState:
    return UnitState(
        name='斥罪',
        faction=Faction.ALLY,
        max_hp=4655,
        atk=916,
        defence=616,
        res=10.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=36,
        redeploy_cd=70.0,
    )
