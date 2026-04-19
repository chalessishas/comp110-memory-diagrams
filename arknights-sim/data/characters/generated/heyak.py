"""霍尔海雅 — generated from ArknightsGameData char_4027_heyak.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4027_heyak
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_heyak() -> UnitState:
    return UnitState(
        name='霍尔海雅',
        faction=Faction.ALLY,
        max_hp=1770,
        atk=723,
        defence=130,
        res=20.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.CASTER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=21,
        redeploy_cd=70.0,
    )
