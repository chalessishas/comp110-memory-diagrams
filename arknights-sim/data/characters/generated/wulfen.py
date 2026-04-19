"""钼铅 — generated from ArknightsGameData char_4171_wulfen.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4171_wulfen
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wulfen() -> UnitState:
    return UnitState(
        name='钼铅',
        faction=Faction.ALLY,
        max_hp=1650,
        atk=560,
        defence=160,
        res=0.0,
        atk_interval=0.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
