"""贾维 — generated from ArknightsGameData char_349_chiave.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_349_chiave
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_chiave() -> UnitState:
    return UnitState(
        name='贾维',
        faction=Faction.ALLY,
        max_hp=1824,
        atk=592,
        defence=342,
        res=0.0,
        atk_interval=1.05,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.VANGUARD,
        attack_type=AttackType.PHYSICAL,
        block=2,
        cost=13,
        redeploy_cd=70.0,
    )
