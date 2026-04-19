"""万顷 — generated from ArknightsGameData char_4119_wanqin.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4119_wanqin
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_wanqin() -> UnitState:
    return UnitState(
        name='万顷',
        faction=Faction.ALLY,
        max_hp=1616,
        atk=514,
        defence=425,
        res=0.0,
        atk_interval=1.3,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=13,
        redeploy_cd=80.0,
    )
