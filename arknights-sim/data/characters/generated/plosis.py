"""白面鸮 — generated from ArknightsGameData char_128_plosis.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_128_plosis
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_plosis() -> UnitState:
    return UnitState(
        name='白面鸮',
        faction=Faction.ALLY,
        max_hp=1610,
        atk=390,
        defence=150,
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
