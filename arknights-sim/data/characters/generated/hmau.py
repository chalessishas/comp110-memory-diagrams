"""吽 — generated from ArknightsGameData char_226_hmau.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_226_hmau
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hmau() -> UnitState:
    return UnitState(
        name='吽',
        faction=Faction.ALLY,
        max_hp=3023,
        atk=442,
        defence=645,
        res=10.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=21,
        redeploy_cd=70.0,
    )
