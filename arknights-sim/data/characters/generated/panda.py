"""食铁兽 — generated from ArknightsGameData char_241_panda.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_241_panda
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_panda() -> UnitState:
    return UnitState(
        name='食铁兽',
        faction=Faction.ALLY,
        max_hp=2145,
        atk=685,
        defence=382,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=20,
        redeploy_cd=70.0,
    )
