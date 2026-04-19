"""阿斯卡纶 — generated from ArknightsGameData char_4132_ascln.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_4132_ascln
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_ascln() -> UnitState:
    return UnitState(
        name='阿斯卡纶',
        faction=Faction.ALLY,
        max_hp=1823,
        atk=954,
        defence=373,
        res=30.0,
        atk_interval=3.5,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=0,
        cost=21,
        redeploy_cd=70.0,
    )
