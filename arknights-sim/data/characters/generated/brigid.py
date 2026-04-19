"""水灯心 — generated from ArknightsGameData char_4177_brigid.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4177_brigid
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_brigid() -> UnitState:
    return UnitState(
        name='水灯心',
        faction=Faction.ALLY,
        max_hp=2350,
        atk=715,
        defence=165,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=17,
        redeploy_cd=80.0,
    )
