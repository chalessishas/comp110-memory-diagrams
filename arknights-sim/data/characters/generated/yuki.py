"""白雪 — generated from ArknightsGameData char_118_yuki.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_118_yuki
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_yuki() -> UnitState:
    return UnitState(
        name='白雪',
        faction=Faction.ALLY,
        max_hp=1630,
        atk=867,
        defence=100,
        res=0.0,
        atk_interval=2.8,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=27,
        redeploy_cd=70.0,
    )
