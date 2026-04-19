"""若叶睦 — generated from ArknightsGameData char_4183_mortis.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4183_mortis
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mortis() -> UnitState:
    return UnitState(
        name='若叶睦',
        faction=Faction.ALLY,
        max_hp=2211,
        atk=792,
        defence=325,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=15,
        redeploy_cd=70.0,
    )
