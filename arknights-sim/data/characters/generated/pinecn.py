"""松果 — generated from ArknightsGameData char_440_pinecn.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_440_pinecn
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_pinecn() -> UnitState:
    return UnitState(
        name='松果',
        faction=Faction.ALLY,
        max_hp=2200,
        atk=722,
        defence=167,
        res=0.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=30,
        redeploy_cd=70.0,
    )
