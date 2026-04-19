"""早露 — generated from ArknightsGameData char_197_poca.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_197_poca
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_poca() -> UnitState:
    return UnitState(
        name='早露',
        faction=Faction.ALLY,
        max_hp=1755,
        atk=1142,
        defence=122,
        res=0.0,
        atk_interval=2.4,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.SNIPER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
