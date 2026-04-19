"""蜜莓 — generated from ArknightsGameData char_449_glider.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_449_glider
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_glider() -> UnitState:
    return UnitState(
        name='蜜莓',
        faction=Faction.ALLY,
        max_hp=1608,
        atk=410,
        defence=107,
        res=10.0,
        atk_interval=2.85,
        move_speed=1.0,
        attack_range_melee=False,
        profession=Profession.MEDIC,
        attack_type=AttackType.HEAL,
        block=1,
        cost=15,
        redeploy_cd=70.0,
    )
