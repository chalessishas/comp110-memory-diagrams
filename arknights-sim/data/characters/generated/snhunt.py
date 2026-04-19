"""雪猎 — generated from ArknightsGameData char_4211_snhunt.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4211_snhunt
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_snhunt() -> UnitState:
    return UnitState(
        name='雪猎',
        faction=Faction.ALLY,
        max_hp=1910,
        atk=1051,
        defence=222,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=19,
        redeploy_cd=70.0,
    )
