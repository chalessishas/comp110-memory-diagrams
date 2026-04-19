"""卡涅利安 — generated from ArknightsGameData char_426_billro.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_426_billro
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_billro() -> UnitState:
    return UnitState(
        name='卡涅利安',
        faction=Faction.ALLY,
        max_hp=2106,
        atk=926,
        defence=258,
        res=15.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=24,
        redeploy_cd=70.0,
    )
