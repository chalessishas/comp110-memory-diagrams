"""卡夫卡 — generated from ArknightsGameData char_214_kafka.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_214_kafka
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_kafka() -> UnitState:
    return UnitState(
        name='卡夫卡',
        faction=Faction.ALLY,
        max_hp=2025,
        atk=525,
        defence=311,
        res=0.0,
        atk_interval=0.93,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.SPECIALIST,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=9,
        redeploy_cd=18.0,
    )
