"""玛恩纳 — generated from ArknightsGameData char_4064_mlynar.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4064_mlynar
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_mlynar() -> UnitState:
    return UnitState(
        name='玛恩纳',
        faction=Faction.ALLY,
        max_hp=4266,
        atk=385,
        defence=502,
        res=15.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=12,
        redeploy_cd=70.0,
    )
