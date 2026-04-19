"""烛煌 — generated from ArknightsGameData char_1040_blaze2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1040_blaze2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_blaze2() -> UnitState:
    return UnitState(
        name='烛煌',
        faction=Faction.ALLY,
        max_hp=1608,
        atk=752,
        defence=131,
        res=15.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.ARTS,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
