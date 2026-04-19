"""荒芜拉普兰德 — generated from ArknightsGameData char_1038_whitw2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1038_whitw2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_whitw2() -> UnitState:
    return UnitState(
        name='荒芜拉普兰德',
        faction=Faction.ALLY,
        max_hp=1503,
        atk=402,
        defence=117,
        res=20.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=22,
        redeploy_cd=70.0,
    )
