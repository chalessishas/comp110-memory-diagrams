"""奥斯塔 — generated from ArknightsGameData char_346_aosta.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_346_aosta
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_aosta() -> UnitState:
    return UnitState(
        name='奥斯塔',
        faction=Faction.ALLY,
        max_hp=2376,
        atk=756,
        defence=192,
        res=0.0,
        atk_interval=2.3,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=31,
        redeploy_cd=70.0,
    )
