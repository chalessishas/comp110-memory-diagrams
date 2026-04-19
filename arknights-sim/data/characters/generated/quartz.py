"""石英 — generated from ArknightsGameData char_4063_quartz.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4063_quartz
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_quartz() -> UnitState:
    return UnitState(
        name='石英',
        faction=Faction.ALLY,
        max_hp=5732,
        atk=1437,
        defence=0,
        res=0.0,
        atk_interval=2.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=22,
        redeploy_cd=70.0,
    )
