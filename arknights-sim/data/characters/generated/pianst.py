"""车尔尼 — generated from ArknightsGameData char_4047_pianst.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4047_pianst
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pianst() -> UnitState:
    return UnitState(
        name='车尔尼',
        faction=Faction.ALLY,
        max_hp=3322,
        atk=665,
        defence=577,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=27,
        redeploy_cd=80.0,
    )
