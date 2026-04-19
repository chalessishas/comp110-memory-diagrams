"""崖心 — generated from ArknightsGameData char_173_slchan.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_173_slchan
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_slchan() -> UnitState:
    return UnitState(
        name='崖心',
        faction=Faction.ALLY,
        max_hp=1970,
        atk=835,
        defence=340,
        res=0.0,
        atk_interval=1.8,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=13,
        redeploy_cd=70.0,
    )
