"""百炼嘉维尔 — generated from ArknightsGameData char_1026_gvial2.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_1026_gvial2
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_gvial2() -> UnitState:
    return UnitState(
        name='百炼嘉维尔',
        faction=Faction.ALLY,
        max_hp=2906,
        atk=816,
        defence=451,
        res=0.0,
        atk_interval=1.2,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.GUARD,
        attack_type=AttackType.PHYSICAL,
        block=3,
        cost=24,
        redeploy_cd=70.0,
    )
