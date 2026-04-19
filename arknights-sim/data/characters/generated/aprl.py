"""四月 — generated from ArknightsGameData char_365_aprl.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_365_aprl
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_aprl() -> UnitState:
    return UnitState(
        name='四月',
        faction=Faction.ALLY,
        max_hp=1280,
        atk=603,
        defence=160,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=70.0,
    )
