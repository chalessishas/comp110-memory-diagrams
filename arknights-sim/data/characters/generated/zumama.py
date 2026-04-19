"""森蚺 — generated from ArknightsGameData char_416_zumama.
Source: E2 max-level, trust 100, no potentials, no module.
Regenerate: python tools/gen_characters.py char_416_zumama
"""
from __future__ import annotations
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Profession


def make_zumama() -> UnitState:
    return UnitState(
        name='森蚺',
        faction=Faction.ALLY,
        max_hp=4468,
        atk=1077,
        defence=685,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.0,
        attack_range_melee=True,
        profession=Profession.DEFENDER,
        attack_type=AttackType.PHYSICAL,
        block=1,
        cost=33,
        redeploy_cd=70.0,
    )
