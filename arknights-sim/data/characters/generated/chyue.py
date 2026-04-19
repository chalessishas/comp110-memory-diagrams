"""重岳 — generated from ArknightsGameData char_2024_chyue.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_2024_chyue
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chyue() -> UnitState:
    return UnitState(
        name='重岳',
        faction=Faction.ALLY,
        max_hp=2635,
        atk=650,
        defence=393,
        res=0.0,
        atk_interval=0.78,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=11,
        redeploy_cd=70.0,
    )
