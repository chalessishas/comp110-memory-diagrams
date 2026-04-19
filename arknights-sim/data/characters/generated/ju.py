"""矩 — generated from ArknightsGameData char_4221_ju.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4221_ju
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ju() -> UnitState:
    return UnitState(
        name='矩',
        faction=Faction.ALLY,
        max_hp=1750,
        atk=1060,
        defence=120,
        res=0.0,
        atk_interval=2.4,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=25,
        redeploy_cd=80.0,
    )
