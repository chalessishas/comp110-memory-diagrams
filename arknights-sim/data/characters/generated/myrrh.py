"""末药 — generated from ArknightsGameData char_117_myrrh.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_117_myrrh
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_myrrh() -> UnitState:
    return UnitState(
        name='末药',
        faction=Faction.ALLY,
        max_hp=1420,
        atk=525,
        defence=131,
        res=0.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=18,
        redeploy_cd=70.0,
    )
