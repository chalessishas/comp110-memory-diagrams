"""芙蓉 — generated from ArknightsGameData char_120_hibisc.
Source: E1 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_120_hibisc
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_hibisc() -> UnitState:
    return UnitState(
        name='芙蓉',
        faction=Faction.ALLY,
        max_hp=1220,
        atk=390,
        defence=110,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=17,
        redeploy_cd=70.0,
    )
