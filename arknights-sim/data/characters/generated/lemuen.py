"""蕾缪安 — generated from ArknightsGameData char_4193_lemuen.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4193_lemuen
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_lemuen() -> UnitState:
    return UnitState(
        name='蕾缪安',
        faction=Faction.ALLY,
        max_hp=1448,
        atk=1301,
        defence=175,
        res=0.0,
        atk_interval=2.7,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=22,
        redeploy_cd=70.0,
    )
